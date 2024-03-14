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
import time

from ansys.hps.client import Client, HPSError, __ansys_apps_version__
from ansys.hps.client.jms import (
    File,
    FloatParameterDefinition,
    JmsApi,
    Job,
    JobDefinition,
    ParameterMapping,
    Project,
    ProjectApi,
    ResourceRequirements,
    Software,
    TaskDefinition,
)

log = logging.getLogger(__name__)


def interrupt_running_task(client, project_id) -> Project:
    jms_api = JmsApi(client)
    proj = jms_api.get_project(project_id)

    project_api = ProjectApi(client, proj.id)

    task_def = project_api.get_task_definitions()[0]

    running_tasks = project_api.get_tasks({"task_definition_id": task_def.id, "eval_status": "running"})
    if not running_tasks:
        log.info("No running Tasks")

    task = running_tasks[0]
    if not task.eval_status == 'running':
        log.info("Task is not running")
        return

    project_url = f"{client.url}/jms/api/v1/projects/{project_id}"
    command_defs_url = f"{project_url}/task_definitions/{task_def.id}/command_definitions"

    resp = client.session.get(command_defs_url)
    command_defs = resp.json()['task_command_definitions']
    
    command_url = f"{project_url}/tasks/{task.id}/commands"
    data_str = f'{{"task_commands" : [{{"name": \"{command_defs[0]["name"]}\", "command_def_id": \"{command_defs[0]["id"]}\", "arguments": {{"immediately": true}}}}]}}'

    resp = client.session.post(command_url, data=data_str)
    if not resp.status_code == 201:
        log.info("Failed to submit Task command")
        return
    
    cmd = resp.json()['task_commands'][0]
    while not cmd['status'] == 'executed' and not cmd['status'] == 'failed':
        resp = client.session.get(command_url, params={"id": cmd['id']})
        if not resp.status_code == 200:
            log.info("Failed to check Task command status")
        cmd = resp.json()['task_commands'][0]
        log.info(f"Command status: {cmd['status']}")
        time.sleep(0.5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-U", "--url", default="https://localhost:8443/hps")
    parser.add_argument("-u", "--username", default="repuser")
    parser.add_argument("-p", "--password", default="repuser")
    parser.add_argument("-P", "--project", required=True)

    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.DEBUG)

    log.debug("=== HPS connection")
    client = Client(url=args.url, username=args.username, password=args.password)

    try:
        log.info(f"HPS URL: {client.url}")
        interrupt_running_task(
            client=client,
            project_id=args.project,
        )
    except HPSError as e:
        log.error(str(e))
