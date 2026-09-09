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

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

import pytest

from ansys.hps.client import (
    HpsMini,
    HpsMiniError,
    HpsMiniStatus,
    create_mini_client,
    find_hps_mini,
    get_hps_mini_status,
)


def test_hps_mini_run_uses_json_output():
    with TemporaryDirectory() as directory:
        mini = Path(directory) / "hps-mini.exe"
        mini.touch()
        data_dir = mini.parent / "state"
        result = Mock(
            returncode=0,
            stdout=json.dumps(
                {
                    "status": "running",
                    "pid": 1234,
                    "url": "http://127.0.0.1:54321",
                    "api_key": "test-key",
                }
            ),
            stderr="",
        )
        completed = Mock(
            returncode=0,
            stdout=result.stdout,
            stderr="",
        )
        with patch("ansys.hps.client.mini.subprocess.run", return_value=completed) as run:
            status = HpsMini(
                executable=mini,
                data_dir=data_dir,
                debug=True,
                verbosity=3,
            ).run()

        assert status == HpsMiniStatus("http://127.0.0.1:54321", "test-key", 1234)
        run.assert_called_once_with(
            [
                str(mini),
                "--data-dir",
                str(data_dir),
                "--debug",
                "--verbosity",
                "3",
                "run",
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=5.0,
        )


def test_hps_mini_run_rejects_stopped_instance():
    with TemporaryDirectory() as directory:
        mini = Path(directory) / "hps-mini.exe"
        mini.touch()
        with patch(
            "ansys.hps.client.mini.subprocess.run",
            return_value=Mock(returncode=0, stdout='{"status":"stopped"}', stderr=""),
        ):
            with pytest.raises(HpsMiniError, match="not running"):
                HpsMini(executable=mini).run()


def test_find_hps_mini_uses_binaries_directory():
    with TemporaryDirectory() as directory:
        working_dir = Path(directory)
        mini = working_dir / "binaries" / "hps-mini.exe"
        mini.parent.mkdir()
        mini.touch()
        with (
            patch.dict("ansys.hps.client.mini.os.environ", {}, clear=True),
            patch("ansys.hps.client.mini.Path.cwd", return_value=working_dir),
            patch("ansys.hps.client.mini.platform.system", return_value="Windows"),
            patch("ansys.hps.client.mini.shutil.which", return_value=None),
        ):
            assert find_hps_mini() == mini


def test_create_mini_client_uses_discovered_connection():
    status = HpsMiniStatus("http://127.0.0.1:54321", "key", 1)
    with (
        patch("ansys.hps.client.mini.HpsMini.run", return_value=status),
        patch("ansys.hps.client.mini.Client") as client_type,
    ):
        create_mini_client(verify=False)

    client_type.assert_called_once_with(
        url="http://127.0.0.1:54321/hps", api_key="key", verify=False
    )


def test_get_hps_mini_status_calls_run():
    status = HpsMiniStatus("http://127.0.0.1:54321", "key", 1)
    with patch("ansys.hps.client.mini.HpsMini.run", return_value=status):
        assert get_hps_mini_status() == status
