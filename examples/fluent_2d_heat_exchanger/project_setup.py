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

"""Example showing how to submit a simple Fluent 2D job to HPS."""

import argparse
import logging
import os

from ansys.hps.client import Client, HPSError, __ansys_apps_version__
from ansys.hps.client.jms import (
    File,
    JmsApi,
    Job,
    JobDefinition,
    Project,
    ProjectApi,
    ResourceRequirements,
    Software,
    TaskDefinition,
)

log = logging.getLogger(__name__)


def create_project(
    client, name, version=__ansys_apps_version__, use_exec_script=False, active=True
) -> Project:
    log.info("=== Create Project")
    jms_api = JmsApi(client)
    proj = Project(name=name, priority=1, active=True)
    proj = jms_api.create_project(proj)

    project_api = ProjectApi(client, proj.id)

    log.info("=== Create Files")
    cwd = os.path.dirname(__file__)

    files = [
        File(
            name="case",
            evaluation_path="heat_exchanger.cas.h5",
            type="application/octet-stream",
            src=os.path.join(cwd, "heat_exchanger.cas.h5"),
        ),
        File(
            name="jou",
            evaluation_path="heat_exchanger.jou",
            type="text/plain",
            src=os.path.join(cwd, "heat_exchanger.jou"),
        ),
        File(
            name="trn", evaluation_path="fluent*.trn", type="text/plain", collect=True, monitor=True
        ),
        File(
            name="output_cas",
            evaluation_path="output_results.cas.h5",
            type="application/octet-stream",
            collect=True,
            monitor=False,
        ),
        File(
            name="output_data",
            evaluation_path="output_results.data.dat.h5",
            type="application/octet-stream",
            collect=True,
            monitor=False,
        ),
    ]

    files = project_api.create_files(files)
    file_ids = {f.name: f.id for f in files}

    log.debug("=== Job Definition with simulation workflow")

    # Task Definition
    task_defs = []
    task_def = TaskDefinition(
        name="Fluent Run",
        software_requirements=[Software(name="Ansys Fluent", version=version)],
        execution_command="%executable% 2d -g -tm %resource:num_cores% -i %file:jou%",
        resource_requirements=ResourceRequirements(
            num_cores=4,
            memory=4000,
            disk_space=500,
            distributed=True,
        ),
        execution_context={
            "dimension": "2d",
        },
        max_execution_time=600.0,
        execution_level=0,
        num_trials=1,
        input_file_ids=[file_ids["case"], file_ids["jou"]],
        output_file_ids=[file_ids["trn"], file_ids["output_cas"], file_ids["output_data"]],
    )

    if use_exec_script:
        task_def.use_execution_script = True
        exec_script_file = project_api.copy_default_execution_script(
            f"fluent-v{version[2:4]}{version[6]}-exec_fluent.py"
        )
        task_def.execution_script_id = exec_script_file.id

    task_defs.append(task_def)

    task_def = project_api.create_task_definitions(task_defs)[0]

    # Create job_definition in project
    job_def = JobDefinition(name="JobDefinition.1", active=True)
    job_def.task_definition_ids = [task_def.id]
    job_def = project_api.create_job_definitions([job_def])[0]

    log.info("=== Submit Job")
    job = project_api.create_jobs(
        [Job(name="Job", eval_status="pending", job_definition_id=job_def.id)]
    )[0]

    log.info(f"Created project '{proj.name}', ID='{proj.id}'")
    log.info(
        f"You can monitor the job status at "
        f"{project_api.client.url}/jms/#/projects/{project_api.project_id}/jobs/{job.id}"
    )

    return proj


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, default="Fluent 2D heat exchanger")
    parser.add_argument("-es", "--use-exec-script", default=False, type=bool)
    parser.add_argument("-U", "--url", default="https://localhost:8443/hps")
    parser.add_argument("-u", "--username", default="repuser")
    parser.add_argument("-p", "--password", default="repuser")
    parser.add_argument("-v", "--ansys-version", default=__ansys_apps_version__)

    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.DEBUG)

    log.debug("=== HPS connection")
    client = Client(url=args.url, username=args.username, password=args.password)

    try:
        log.info(f"HPS URL: {client.url}")
        proj = create_project(
            client=client,
            name=args.name,
            version=args.ansys_version,
            use_exec_script=args.use_exec_script,
        )
    except HPSError as e:
        log.error(str(e))
