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

"""Simple script to use RCS for registering and unregistering an instance."""

import argparse
import logging

from ansys.hps.client import Client, HPSError
from ansys.hps.client.rcs import RcsApi, RegisterInstance, UnRegisterInstance

log = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-U", "--url", default="https://localhost:8443/hps")
    parser.add_argument("-u", "--username", default="repuser")
    parser.add_argument("-p", "--password", default="repuser")
    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    try:
        log.info("Connect to HPC Platform Services")
        client = Client(url=args.url, username=args.username, password=args.password)
        log.info(f"HPS URL: {client.url}")
    except HPSError as e:
        log.error(str(e))

    rcs_api = RcsApi(client)
    request_data = {
        "url": f"{args.url}/rcs",
        "service_name": "solver",
        "jms_project_id": "1234",
        "jms_job_id": "5678",
        "jms_task_id": "91011",
        "routing": "path_prefix",
    }
    resp = rcs_api.health_check()
    log.info(f"RCS API health check: {resp}")
    log.info("Register instance")
    register_instance = rcs_api.register_instance(RegisterInstance(**request_data))
    log.info(f"Register instance response: {register_instance}")
    log.info("Unregister instance")
    unregister = {"resource_name": register_instance.resource_name}
    unregister_instance = rcs_api.unregister_instance(UnRegisterInstance(**unregister))
    log.info(f"Unregister instance response: {unregister_instance}")
