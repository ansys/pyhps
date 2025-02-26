# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
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
from pprint import pprint
import time

from ansys.rep.common.auth.self_signed_token_provider import SelfSignedTokenProvider
import jwt
from marshmallow.utils import missing

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
    projects_raw = jms_api.get_projects(
        as_objects=False, statistics=True, permissions=True, sort="-modification_time"
    )
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
        modified_age = (datetime.now(timezone.utc) - project.modification_time).total_seconds()
        if len(filtered_projects) > 10 and modified_age > 48 * 60 * 60:
            continue  # Skip projects older than 2 days

        created_age = (datetime.now(timezone.utc) - project.creation_time).total_seconds()
        age_hours = int(created_age / 3600)
        age_minutes = int((created_age % 3600) / 60)
        log.debug("")
        log.debug(f"    Project: ({age_hours}h {age_minutes}m old) {project.name}: {project.id}")
        permissions = [d["value_name"] for d in find_by_id(projects_raw, project.id)["permissions"]]
        log.debug(f"    Permissions: {permissions}")

        proj_api = ProjectApi(client, project.id)
        try:
            if remove is not None:
                if "old" in remove:
                    # Old remove old projects based on time alone
                    if age_hours > 48:
                        log.debug(f"    === Removing project older than 2 days: age {age_hours}h.")
                        jms_api.delete_project(project)
                        continue
                if check_project_stats(project, [], ["running", "evaluated", "failed"], False):
                    # Remove more recent projects that are broken (No running or finished tasks)
                    if check_project_stats(project, [], ["pending"]):
                        # Project with no tasks in any valid state (pend, run, finish)
                        if age_hours > 1:
                            log.debug(
                                f"    === Removing project not pending, running: age {age_hours}h."
                            )
                            jms_api.delete_project(project)
                            continue
                    else:
                        # Project with pending for a long time (error in setup or cluster)
                        if age_hours > 6:
                            log.debug(
                                f"    === Removing project pending for 1/2 day: age {age_hours}h."
                            )
                            jms_api.delete_project(project)
                            continue
            tasks = proj_api.get_tasks()
            if len(tasks) > 0:
                log.debug(f"    === Tasks {filter_dict(project.statistics['eval_status'])}")
            else:
                log.debug("    === No Tasks")
            for task in tasks:
                resources = task.task_definition_snapshot.resource_requirements
                log.debug(
                    f"{' '*8}{task.task_definition_snapshot.name}:{task.job_id}->{task.eval_status}"
                )
                if task.eval_status == "running":
                    log.debug(f"{' '*10}Running on evaluator: {task.host_id}")
                if resources not in [None, missing]:
                    queue = (
                        resources.hpc_resources.queue
                        if resources.hpc_resources not in [None, missing]
                        else "NotSet"
                    )
                    log.debug(f"{' '*10}CRS: {resources.compute_resource_set_id} -> {queue}")

                """
                log.debug(f"{' '*10}Files:")
                files = proj_api.get_files(id=task.output_file_ids)
                file_counts = {}
                for f in files:
                    if f.name in file_counts:
                        file_counts[f.name] += 1
                    else:
                        file_counts[f.name] = 1

                incomplete = False
                for file_name, count in file_counts.items():
                    file = next(f for f in files if f.name == file_name)
                    # and f.storage_id in [None, missing])
                    # print(file)
                    if count > 3:
                        log.debug(f"{' '*12}{file_name}:{file.format} -> {count} times")
                    line = f"{' '*12}---"
                    counter = 0
                    for f in [f for f in files if f.name == file_name]:
                        counter += 1
                        line += f" {f.evaluation_path[:20].rjust(20)}"
                        line += f" -{f.size}b-{f.type.split('/')[0][:6].ljust(6)} "
                        incomplete = True
                        if counter % 4 == 0:
                            log.debug(line)
                            line = f"{' '*12}---"
                            incomplete = False
                if incomplete:
                    log.debug(line)
                """
        except HPSError as e:
            log.debug(e)
            continue


def show_rms_data(client: Client, verbose: bool) -> Project:
    rms_api = RmsApi(client)
    try:
        scalers = rms_api.get_scalers()
        log.debug("=== Scalers")
        pprint(scalers)
        crs_sets = rms_api.get_compute_resource_sets()
        log.debug("")
        log.debug("=== CRS Sets")
        for crs in crs_sets:
            log.debug(f"    === {crs.name}: {crs.backend.plugin_name} -> {crs.id}")
            scaler = find_by_id(scalers, crs.scaler_id)
            if scaler:
                log.debug(
                    f"    === Scaler info: {crs.scaler_id}: {scaler.host_id}"
                    + f" {scaler.host_name} {scaler.build_info}"
                )
            else:
                log.debug(f"    === Scaler info: {crs.scaler_id}: NOT FOUND")

            log.debug(f"   Config: {crs.backend.json()}")
            try:
                info = rms_api.get_cluster_info(crs.id)
            except:
                log.warning(f"       Cluster info not available for {crs.name}")
                log.debug("")
                continue
            for queue in info.queues:
                log.debug(f"        === {queue.name}:")
                if verbose:
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
                        # log.debug(f"Found user_id from token: {payload['sub']}")
                    provider = SelfSignedTokenProvider({"hps-default": args.signing_key})
                    if account:
                        extra = {"account_admin": True, "oid": user_id}
                    else:
                        extra = {"service_admin": True, "oid": user_id}
                    token = provider.generate_signed_token(user_id, user_id, account, 6000, extra)
                    # log.debug(f"Token: {token}")
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


def run_main_and_monitor(log, monitor_projects, show_rms_data, _main, args):
    errors = {}
    runtime_errors = 0
    exceptions = 0
    start_time = datetime.now()
    while True:
        try:
            _main(log, monitor_projects, show_rms_data, args)
        except Exception as e:
            exception = str(e)
            log.error(exception)
            key = exception[:150]
            if key in errors:
                errors[key][str(datetime.now())] = exception
            else:
                errors[key] = {str(datetime.now()): exception}

        log.info("")
        log.info(f"=== Logged errors")
        for error, times in errors.items():
            log.info(f"---> {next(times.items())}")
            log.info(f"---> ---> {len(times)} times @ {times}")
        time.sleep(10)


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
        run_main_and_monitor(log, monitor_projects, show_rms_data, _main, args)
    else:
        _main(log, monitor_projects, show_rms_data, args)
