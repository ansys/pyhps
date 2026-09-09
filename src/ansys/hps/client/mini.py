# Copyright (C) 2022 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Helpers for connecting PyHPS to a local hps-mini instance."""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .client import Client
from .exceptions import ClientError

MINI_PATH_ENV = "HPS_MINI_PATH"
MINI_DATA_DIR_ENV = "HPS_MINI_DATA_DIR"


class HpsMiniError(ClientError):
    """Raised when a local hps-mini instance cannot be discovered."""


@dataclass(frozen=True)
class HpsMiniStatus:
    """Connection details reported by hps-mini status."""

    url: str
    api_key: str
    pid: int


class HpsMini:
    """Discover and connect to a running hps-mini instance."""

    def __init__(
        self,
        executable: str | os.PathLike[str] | None = None,
        data_dir: str | os.PathLike[str] | None = None,
        timeout: float = 5.0,
        debug: bool = False,
        verbosity: int | None = None,
    ):
        """Initialize a local hps-mini connection helper."""
        self.executable = executable
        self.data_dir = data_dir
        self.timeout = timeout
        self.debug = debug
        self.verbosity = verbosity

    def find(self) -> Path:
        """Find the hps-mini executable."""
        candidate = self.executable or os.environ.get(MINI_PATH_ENV)
        if candidate:
            path = Path(candidate).expanduser()
            if path.is_file():
                return path
            raise HpsMiniError(f"hps-mini executable not found at {path}")

        names = mini_executable_names()
        for path in mini_default_paths(names):
            if path.is_file():
                return path
        for name in names:
            resolved = shutil.which(name)
            if resolved:
                return Path(resolved)
        raise HpsMiniError(
            "hps-mini executable was not found; set HPS_MINI_PATH, place it in the current "
            "directory or ./binaries, or add hps-mini to PATH"
        )

    def run(self) -> HpsMiniStatus:
        """Start hps-mini if needed and return its connection status."""
        mini = self.find()
        configured_data_dir = self.data_dir or os.environ.get(MINI_DATA_DIR_ENV)
        command = [str(mini)]
        if configured_data_dir:
            command.extend(["--data-dir", str(Path(configured_data_dir).expanduser())])
        if self.debug:
            command.append("--debug")
        if self.verbosity is not None:
            command.extend(["--verbosity", str(self.verbosity)])
        command.extend(["run", "--json"])

        try:
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise HpsMiniError(f"could not query hps-mini: {error}") from error

        output = result.stdout.strip()
        try:
            payload = json.loads(output)
        except json.JSONDecodeError as error:
            detail = result.stderr.strip() or output or "no output"
            raise HpsMiniError(f"invalid hps-mini status output: {detail}") from error

        if payload.get("status") != "running":
            raise HpsMiniError("hps-mini is not running")

        url = payload.get("url")
        api_key = payload.get("api_key", "")
        pid = payload.get("pid")
        if not isinstance(url, str) or not url:
            raise HpsMiniError("hps-mini status did not include a URL")
        if not isinstance(api_key, str):
            raise HpsMiniError("hps-mini status returned an invalid API key")
        if not isinstance(pid, int):
            raise HpsMiniError("hps-mini status returned an invalid PID")
        if result.returncode != 0:
            raise HpsMiniError(f"hps-mini status failed with exit code {result.returncode}")

        return HpsMiniStatus(url=url, api_key=api_key, pid=pid)

    def client(self, **kwargs) -> Client:
        """Create a PyHPS client connected to the running hps-mini instance."""
        status = self.run()
        url = status.url.rstrip("/") + "/hps"
        return Client(url=url, api_key=status.api_key or None, **kwargs)


def find_hps_mini(executable: str | os.PathLike[str] | None = None) -> Path:
    """Find the hps-mini executable."""
    return HpsMini(executable=executable).find()


def mini_executable_names() -> tuple[str, ...]:
    """Return hps-mini executable names supported by the current platform."""
    if platform.system() == "Windows":
        return "hps-mini.exe", "hps-mini"
    return ("hps-mini",)


def mini_default_paths(names: tuple[str, ...]) -> tuple[Path, ...]:
    """Return common hps-mini locations relative to the current directory."""
    working_dir = Path.cwd()
    return tuple(
        path for name in names for path in (working_dir / name, working_dir / "binaries" / name)
    )


def get_hps_mini_status(
    executable: str | os.PathLike[str] | None = None,
    data_dir: str | os.PathLike[str] | None = None,
    timeout: float = 5.0,
    debug: bool = False,
    verbosity: int | None = None,
) -> HpsMiniStatus:
    """Query a running hps-mini instance."""
    return HpsMini(
        executable=executable,
        data_dir=data_dir,
        timeout=timeout,
        debug=debug,
        verbosity=verbosity,
    ).run()


def create_mini_client(
    executable: str | os.PathLike[str] | None = None,
    data_dir: str | os.PathLike[str] | None = None,
    timeout: float = 5.0,
    debug: bool = False,
    verbosity: int | None = None,
    **kwargs,
) -> Client:
    """Create a PyHPS client connected to the running hps-mini instance."""
    return HpsMini(
        executable=executable,
        data_dir=data_dir,
        timeout=timeout,
        debug=debug,
        verbosity=verbosity,
    ).client(**kwargs)
