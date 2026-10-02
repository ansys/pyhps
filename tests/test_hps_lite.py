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
    HpsLite,
    HpsLiteError,
    HpsLiteStatus,
    create_hps_lite_client,
    find_hps_lite,
    get_hps_lite_status,
)
from ansys.hps.client.hps_lite import hps_lite_executable_name


def test_hps_lite_run_uses_json_output():
    with TemporaryDirectory() as directory:
        hps_lite = Path(directory) / "hps-lite.exe"
        hps_lite.touch()
        data_dir = hps_lite.parent / "state"
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
        with patch("ansys.hps.client.hps_lite.subprocess.run", return_value=completed) as run:
            status = HpsLite(
                executable=hps_lite,
                data_dir=data_dir,
                debug=True,
                verbosity=3,
            ).run()

        assert status == HpsLiteStatus("http://127.0.0.1:54321", "test-key", 1234)
        run.assert_called_once_with(
            [
                str(hps_lite),
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
            timeout=30.0,
        )


def test_hps_lite_run_rejects_stopped_instance():
    with TemporaryDirectory() as directory:
        hps_lite = Path(directory) / "hps-lite.exe"
        hps_lite.touch()
        with patch(
            "ansys.hps.client.hps_lite.subprocess.run",
            return_value=Mock(returncode=0, stdout='{"status":"stopped"}', stderr=""),
        ):
            with pytest.raises(HpsLiteError, match="not running"):
                HpsLite(executable=hps_lite).run()


def test_find_hps_lite_uses_binaries_directory():
    with TemporaryDirectory() as directory:
        working_dir = Path(directory)
        hps_lite = working_dir / "binaries" / "hps-lite.exe"
        hps_lite.parent.mkdir()
        hps_lite.touch()
        with (
            patch.dict("ansys.hps.client.hps_lite.os.environ", {}, clear=True),
            patch("ansys.hps.client.hps_lite.Path.cwd", return_value=working_dir),
            patch("ansys.hps.client.hps_lite.platform.system", return_value="Windows"),
            patch("ansys.hps.client.hps_lite.shutil.which", return_value=None),
        ):
            assert find_hps_lite() == hps_lite


def test_hps_lite_executable_name_returns_single_platform_name():
    with patch("ansys.hps.client.hps_lite.platform.system", return_value="Windows"):
        assert hps_lite_executable_name() == "hps-lite.exe"

    with patch("ansys.hps.client.hps_lite.platform.system", return_value="Linux"):
        assert hps_lite_executable_name() == "hps-lite"


def test_create_hps_lite_client_uses_discovered_connection():
    status = HpsLiteStatus("http://127.0.0.1:54321", "key", 1)
    with (
        patch("ansys.hps.client.hps_lite.HpsLite.run", return_value=status),
        patch("ansys.hps.client.hps_lite.Client") as client_type,
    ):
        create_hps_lite_client(verify=False)

    client_type.assert_called_once_with(
        url="http://127.0.0.1:54321/hps", api_key="key", verify=False
    )


def test_get_hps_lite_status_calls_run():
    status = HpsLiteStatus("http://127.0.0.1:54321", "key", 1)
    with patch("ansys.hps.client.hps_lite.HpsLite.run", return_value=status):
        assert get_hps_lite_status() == status
