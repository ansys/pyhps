# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""
Example to submit a nonlinear tire analysis job to HPS.

This is the Ansys Parametric Design Language (APDL) Tire Performance Simulation example included
in the technology demonstration guide (td-57).
"""

import argparse
import logging

from ansys.hps.client import Client, HPSError
from ansys.hps.client.jms import JmsApi, Project
from ansys.hps.client.rms import RmsApi

log = logging.getLogger(__name__)


def show_rms_data(client: Client, verbose: bool) -> Project:

    rms_api = RmsApi(client)
    try:
        crs_sets = rms_api.get_compute_resource_sets()
        log.debug("")
        log.debug("=== CRS Sets")
        for crs in crs_sets:
            log.debug(f"    === {crs.name}: {crs.backend.plugin_name}")
            if verbose:
                try:
                    info = rms_api.get_cluster_info(crs.id)
                except:
                    log.warning(f"       Cluster info not available for {crs.name}")
                    log.debug("")
                    continue
                for queue in info.queues:
                    log.debug(f"        === {queue.name}:")
                    for prop in queue.additional_props:
                        log.debug(f"            {prop}: {queue.additional_props[prop]}")
    except HPSError as e:
        log.error(str(e))
        log.error(e.response.content)

    log.debug("")
    log.debug("")
    log.debug("=== Projects")
    jms_api = JmsApi(client)
    projects = jms_api.get_projects()

    for project in projects:
        log.debug(f"    {project.name}: {project.id}")

    log.debug("")
    log.debug("")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-U", "--urls", nargs="+", default="https://localhost:8443/hps")
    parser.add_argument("-u", "--username", default="repuser")
    parser.add_argument("-p", "--password", default="repuser")
    parser.add_argument("-t", "--token", default="")
    parser.add_argument("-a", "--accounts", nargs="+", default="onprem_account")
    parser.add_argument("-v", "--verbose", default=False)

    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.DEBUG)

    for url in args.urls:
        for account in args.accounts:
            if args.token:
                client = Client(url=url, access_token=args.token)
                client.session.headers.update({"accountid": account})
            else:
                client = Client(url=url, username=args.username, password=args.password)

            try:
                log.info("")
                log.info(f"=== Url Specified     : {client.url}")
                log.info(f"=== Account Specified : {account}")
                proj = show_rms_data(client=client, verbose=args.verbose)
            except HPSError as e:
                log.error(str(e))
