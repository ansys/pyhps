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

# /// script
# requires-python = "==3.10"
# dependencies = [
#     "ansys-hps-client @ git+https://github.com/ansys/pyhps.git@main"
# ]
# ///

import argparse
import logging
import os

from ansys.hps.client import Client, HPSError
from ansys.hps.client.jms import (
    File,
    JmsApi,
    Job,
    JobDefinition,
    Project,
    ProjectApi,
    ResourceRequirements,
    Software,
    SuccessCriteria,
    TaskDefinition,
)

log = logging.getLogger(__name__)


def create_project(client, num_jobs):
    log.debug("=== Create Project")
    jms_api = JmsApi(client)
    proj = jms_api.create_project(
        Project(
            name=f"Python UV example - {num_jobs} jobs",
            priority=1,
            active=True,
        ),
        replace=True,
    )
    project_api = ProjectApi(client, proj.id)

    log.debug("=== Define Files")
    cwd = os.path.dirname(__file__)
    # Input Files
    files = [
        File(
            name="eval",
            evaluation_path="eval.py",
            type="text/plain",
            src=os.path.join(cwd, "eval.py"),
        ),
        File(
            name="exec_script",
            evaluation_path="exec_script.py",
            type="text/plain",
            src=os.path.join(cwd, "exec_script.py"),
        ),
        File(
            name="plot",
            evaluation_path="plot.png",
            type="image/png",
            collect=True,
        ),
    ]
    files = project_api.create_files(files)
    file_ids = {f.name: f.id for f in files}

    log.debug("=== Define Task")
    task_def = TaskDefinition(
        name="plotting",
        software_requirements=[Software(name="Uv")],
        resource_requirements=ResourceRequirements(
            num_cores=0.5,
            memory=100 * 1024 * 1024,  # 100 MB
            disk_space=10 * 1024 * 1024,  # 10 MB
        ),
        execution_level=0,
        max_execution_time=500.0,
        use_execution_script=True,
        execution_script_id=file_ids["exec_script"],
        execution_command="%executable% run %file:eval%",
        input_file_ids=[file_ids["eval"]],
        output_file_ids=[file_ids["plot"]],
        success_criteria=SuccessCriteria(
            return_code=0,
            require_all_output_files=True,
        ),
    )
    task_defs = project_api.create_task_definitions([task_def])

    print("== Define Job")
    job_def = JobDefinition(
        name="JobDefinition.1", active=True, task_definition_ids=[task_defs[0].id]
    )
    job_def = project_api.create_job_definitions([job_def])[0]
    log.debug(f"== Create {num_jobs} Jobs")
    jobs = []
    for i in range(num_jobs):
        jobs.append(Job(name=f"Job.{i}", eval_status="pending", job_definition_id=job_def.id))
    project_api.create_jobs(jobs)
    log.info(f"Created project '{proj.name}', ID='{proj.id}'")
    return proj


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--num-jobs", type=int, default=10)
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
        proj = create_project(
            client=client,
            num_jobs=args.num_jobs,
        )

    except HPSError as e:
        log.error(str(e))
