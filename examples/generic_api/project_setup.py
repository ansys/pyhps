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
from datetime import datetime, timezone
import json
import logging
import time

from ansys.rep.common.auth.self_signed_token_provider import SelfSignedTokenProvider
import jwt

from ansys.hps.client import Client, HPSError
from ansys.hps.client.jms import JmsApi, Project, ProjectApi
from ansys.hps.client.jms.resource.project import ProjectSchema
from ansys.hps.client.rms import RmsApi

log = logging.getLogger(__name__)


def monitor_projects(client: Client, verbose: bool, filter: str, remove: str = None):
    log.debug("")
    log.debug("")
    jms_api = JmsApi(client)
    projects = jms_api.get_projects(statistics=True)

    filtered_projects = projects
    if filter is not None:
        log.debug(f"Filtering projects based on name including: {filter}")
        filtered_projects = [
            proj for proj in projects if proj.name.lower().find(filter.lower()) >= 0
        ]

    log.debug(f"=== Projects ({len(filtered_projects)})")
    for project in filtered_projects:
        age = (datetime.now(timezone.utc) - project.creation_time).total_seconds()
        age_hours = int(age / 3600)
        log.debug("")
        log.debug(f"    Project: ({age_hours}h old) {project.name}: {project.id}")
        proj_api = ProjectApi(client, project.id)

        tasks = proj_api.get_tasks()
        if len(tasks) > 0:
            log.debug(f"    === Tasks {project.statistics['eval_status']}")
        else:
            log.debug("    === No Tasks")
        if remove is not None:
            if "old" in remove:
                if age_hours > 120:
                    log.debug(f"    === Removing project older than 5 days: age {age_hours}h.")
                    jms_api.delete_project(project)
            if project.statistics["eval_status"]["pending"] == 0:
                if project.statistics["eval_status"]["running"] == 0:
                    if age_hours > 1:
                        log.debug(
                            f"    === Removing project not pending or running: age {age_hours}h."
                        )
                        jms_api.delete_project(project)
                        continue
        for task in tasks:
            log.debug(f"        {task.task_definition_snapshot.name} -> {task.eval_status}")


def show_rms_data(client: Client, verbose: bool) -> Project:
    rms_api = RmsApi(client)
    try:
        crs_sets = rms_api.get_compute_resource_sets()
        log.debug("")
        log.debug("=== CRS Sets")
        for crs in crs_sets:
            log.debug(f"    === {crs.name}: {crs.backend.plugin_name}")
            if verbose:
                log.debug(f"   Config: {crs.backend.json()}")
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

    schema = ProjectSchema()
    project = Project(name="testing", priority=1, active=False)
    serialized_data = schema.dump(project)
    log.debug(json.dumps({"projects": [serialized_data], "replace": True}))

    log.debug("")
    log.debug("")


def _main(log, monitor_latest_project, show_rms_data, args):
    for url in args.urls:
        accounts = args.accounts
        if not any(args.accounts):
            accounts = [None]
        for account in accounts:
            if args.token or args.signing_key:
                if args.signing_key:
                    user_id = "client_service"
                    if args.user_id:
                        user_id = args.user_id
                    elif args.token:
                        payload = jwt.decode(
                            args.token, algorithms=["RS256"], options={"verify_signature": False}
                        )
                        user_id = payload["sub"]
                        log.debug(f"Found user_id from token: {payload['sub']}")
                    provider = SelfSignedTokenProvider({"hps-default": args.signing_key})
                    token = provider.generate_signed_token(
                        user_id,
                        "dummy_client" if account else account,
                        account,
                        6000,
                        {"oid": user_id},
                    )
                else:
                    token = args.token
                client = Client(url=url, access_token=token, verify=True)
                if account:
                    client.session.headers.update({"accountid": account})
            else:
                client = Client(url=url, username=args.username, password=args.password)

            try:
                log.info("")
                log.info(f"=== Url Specified     : {client.url}")
                log.info(f"=== Account Specified : {account}")
                if args.monitor:
                    monitor_latest_project(
                        client=client, verbose=args.verbose, filter=args.filter, remove=args.remove
                    )
                else:
                    show_rms_data(client=client, verbose=args.verbose)

            except HPSError as e:
                log.error(str(e))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-U", "--urls", nargs="+", default="https://localhost:8443/hps")
    parser.add_argument("-u", "--username", default="repuser")
    parser.add_argument("-p", "--password", default="repuser")
    parser.add_argument("-t", "--token", default="")
    parser.add_argument("-a", "--accounts", nargs="+", default="")
    parser.add_argument("-v", "--verbose", default=False)
    parser.add_argument("-m", "--monitor", default=False)
    parser.add_argument("-s", "--signing_key", default="")
    parser.add_argument("-i", "--user_id", default="")
    parser.add_argument("-f", "--filter", default=None)
    parser.add_argument("-r", "--remove", default=None)

    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.DEBUG)

    if args.monitor:
        while True:
            _main(log, monitor_projects, show_rms_data, args)
            time.sleep(10)
    else:
        _main(log, monitor_projects, show_rms_data, args)
