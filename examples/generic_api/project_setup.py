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
from ansys.hps.client.jms.resource.project import Project, ProjectSchema
from ansys.hps.client.rms import RmsApi

log = logging.getLogger(__name__)


def filter_dict(input_dict, desired_keys=["evaluated", "pending", "failed", "running"]):
    """
    Filters the input dictionary to only include the keys in desired_keys.

    Args:
    input_dict (dict): The dictionary to filter.
    desired_keys (list): A list of keys to retain in the filtered dictionary.

    Returns:
    dict: A new dictionary containing only the desired keys.
    """
    return {key: input_dict[key] for key in desired_keys if key in input_dict}


def find_by_id(object_list, target_id):
    """
    Find an object in a list by its ID.

    :param object_list: List of objects (dictionaries or custom objects) to search.
    :param target_id: The ID to search for.
    :return: The object if found, otherwise None.
    """
    for obj in object_list:
        if isinstance(obj, dict) and "id" in obj:
            if obj["id"] == target_id:
                return obj
        elif hasattr(obj, "id"):
            if obj.id == target_id:
                return obj
    return None


def check_project_stats(
    proj: Project, greater_than_zero: list[str], equal_zero: list[str], empty_value=True
) -> bool:
    # If no stats yet, then dont remove it...
    if not "pending" in proj.statistics["eval_status"]:
        return empty_value

    for item in greater_than_zero:
        if proj.statistics["eval_status"][item] <= 0:
            return False

    for item in equal_zero:
        if proj.statistics["eval_status"][item] > 0:
            return False

    return True


def monitor_projects(
    client: Client, verbose: bool, filter: str, remove: str = None, limited_monitoring: bool = False
):
    log.debug("")
    log.debug("")
    jms_api = JmsApi(client)
    projects_raw = jms_api.get_projects(as_objects=False, statistics=True, permissions=True)
    schema = ProjectSchema(many=True)
    projects: list[Project] = schema.load(projects_raw)

    filtered_projects = projects
    if filter is not None:
        log.debug(f"Filtering projects based on name including: {filter}")
        filtered_projects = [
            proj for proj in projects if proj.name.lower().find(filter.lower()) >= 0
        ]

    if limited_monitoring:
        log.debug(f"Limited monitoring enabled: Showing only states pending/running/failed not 0")
        filtered_projects = [
            p
            for p in list(filtered_projects)
            if not check_project_stats(p, [], ["failed", "running", "pending"])
        ]

    log.debug(f"=== Projects ({len(filtered_projects)})")
    for project in filtered_projects:
        age = (datetime.now(timezone.utc) - project.creation_time).total_seconds()
        age_hours = int(age / 3600)
        log.debug("")
        log.debug(f"    Project: ({age_hours}h old) {project.name}: {project.id}")
        permissions = [d["value_name"] for d in find_by_id(projects_raw, project.id)["permissions"]]
        log.debug(f"    Permissions: {permissions}")
        proj_api = ProjectApi(client, project.id)

        tasks = proj_api.get_tasks()
        if len(tasks) > 0:
            log.debug(f"    === Tasks {filter_dict(project.statistics['eval_status'])}")
        else:
            log.debug("    === No Tasks")
        if remove is not None:
            if "old" in remove:
                # Old remove old projects based on time alone
                if age_hours > 72:
                    log.debug(f"    === Removing project older than 3 days: age {age_hours}h.")
                    jms_api.delete_project(project)
                    continue
            elif check_project_stats(project, [], ["running", "evaluated", "failed"], False):
                # Remove more recent projects that are broken (No running or finished tasks)
                if check_project_stats(project, [], ["pending"]):
                    # Project with no tasks in any valid state (pend, run, finish)
                    if age_hours > 1:
                        log.debug(
                            f"    === Removing project not pending or running: age {age_hours}h."
                        )
                        jms_api.delete_project(project)
                        continue
                else:
                    # Project with pending for a long time (error in setup or cluster)
                    if age_hours > 12:
                        log.debug(
                            f"    === Removing project pending for 1/2 day: age {age_hours}h."
                        )
                        jms_api.delete_project(project)
                        continue
        for task in tasks:
            log.debug(
                f"        {task.task_definition_snapshot.name}: {task.job_id} -> {task.eval_status}"
            )


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
                client = Client(
                    url=url, access_token=token, verify=False if args.skip_verify else True
                )
                if account:
                    client.session.headers.update({"accountid": account})
            else:
                client = Client(
                    url=url,
                    username=args.username,
                    password=args.password,
                    verify=False if args.skip_verify else True,
                )

            try:
                log.info("")
                log.info(f"=== Url Specified     : {client.url}")
                log.info(f"=== Account Specified : {account}")
                if args.monitor or args.limited_monitor:
                    monitor_latest_project(
                        client=client,
                        verbose=args.verbose,
                        filter=args.filter,
                        remove=args.remove,
                        limited_monitoring=args.limited_monitor,
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
    parser.add_argument("-l", "--limited_monitor", default=False)
    parser.add_argument("-s", "--signing_key", default="")
    parser.add_argument("-i", "--user_id", default="")
    parser.add_argument("-f", "--filter", default=None)
    parser.add_argument("-r", "--remove", default=None)

    parser.add_argument("--skip_verify", default=True, action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.DEBUG)

    if args.monitor or args.limited_monitor:
        while True:
            _main(log, monitor_projects, show_rms_data, args)
            time.sleep(10)
    else:
        _main(log, monitor_projects, show_rms_data, args)
