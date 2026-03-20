# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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
import logging

import pytest

from ansys.hps.client import Client
from ansys.hps.client.jms import JmsApi
from ansys.hps.client.rms import RmsApi

log = logging.getLogger(__name__)


@pytest.mark.order(1)
def test_services(client: Client, build_info_path: str):
    # make sure services are up and running, print info

    # check jms api
    jms_api = JmsApi(client)
    jms_info = jms_api.get_api_info()
    log.info(f"JMS api info\n{json.dumps(jms_info, indent=2)}")
    assert "build" in jms_info
    assert "services" in jms_info
    assert "auth_url" in jms_info["services"]
    assert "settings" in jms_info
    assert "execution_script_bucket" in jms_info["settings"]
    assert "execution_script_default_bucket" in jms_info["settings"]

    # check dts api
    r = client.session.get(f"{client.url}/dt/api/v1")
    dt_info = r.json()
    log.info(f"Dt api info\n{json.dumps(dt_info, indent=2)}")
    assert "build_info" in dt_info

    # check rms api
    rms_api = RmsApi(client)
    rms_info = rms_api.get_api_info()
    log.info(f"RMS api info\n{json.dumps(rms_info, indent=2)}")
    assert "build" in rms_info
    assert "version" in rms_info["build"]

    info = {"jms": jms_info, "dt": dt_info, "rms": rms_info}
    with open(build_info_path, "w") as f:
        f.write(json.dumps(info, indent=2))

    with open(build_info_path.replace(".json", ".md"), "w") as f:
        f.write("### Build info")
        f.write("\n```json\n")
        f.write(json.dumps(info, indent=2))
        f.write("\n```")
