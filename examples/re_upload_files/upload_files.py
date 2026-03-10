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

"""Example to retry upload of failed Evaluator upload."""

import argparse
import logging
import os

from ansys.hps.client import Client, HPSError
from ansys.hps.client.jms import JmsApi, ProjectApi

log = logging.getLogger(__name__)


def upload_files(client, project_id, upload_file):
    """Upload files example."""

    jms_api = JmsApi(client)
    project = jms_api.get_project(id=project_id)

    log.info(f"Project id: {project.id}")
    project_api = ProjectApi(client, project.id)

    log.info("=== Example: Uploading output files using ProjectApi.re_upload_files()")
    project_api.re_upload_files(upload_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-id", "--id", type=str, default="")
    parser.add_argument("-f", "--file", type=str, default="")
    parser.add_argument("-U", "--url", default="https://127.0.0.1:8443/hps")
    parser.add_argument("-u", "--username", default="repadmin")
    parser.add_argument("-p", "--password", default="repadmin")
    parser.add_argument("-t", "--token", default="")
    parser.add_argument("-a", "--account", default="onprem_account")
    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    try:
        log.info("Connect to HPC Platform Services")

        if args.token:
            client = Client(url=args.url, access_token=args.token)
            client.session.headers.update({"accountid": args.account})
        else:
            client = Client(url=args.url, username=args.username, password=args.password)
        log.info(f"HPS URL: {client.url}")

        file_path = args.file
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getcwd(), file_path)
            file_path = os.path.abspath(file_path)

        upload_files(client=client, project_id=args.id, upload_file=file_path)

    except HPSError as e:
        log.error(str(e))
