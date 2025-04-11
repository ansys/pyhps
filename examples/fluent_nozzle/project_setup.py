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

"""Example script to set up a simple Fluent project in PyHPS."""

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
    SuccessCriteria,
    TaskDefinition,
)

log = logging.getLogger(__name__)


def create_project(client, name, num_jobs=20, version=__ansys_apps_version__):
    """Create an HPS project consisting of an Ansys Fluent model."""
    jms_api = JmsApi(client)
    log.debug("=== Project")
    proj = Project(name=name, priority=1, active=True)
    proj = jms_api.create_project(proj, replace=True)

    project_api = ProjectApi(client, proj.id)

    log.debug("=== Files")
    cwd = os.path.dirname(__file__)
    files = []
    files.append(
        File(
            name="case",
            evaluation_path="nozzle.cas",
            type="application/octet-stream",
            src=os.path.join(cwd, "nozzle.cas"),
        )
    )
    files.append(
        File(
            name="jou",
            evaluation_path="solve.jou",
            type="text/plain",
            src=os.path.join(cwd, "solve.jou"),
        )
    )

    files.append(
        File(
            name="trn", evaluation_path="fluent*.trn", type="text/plain", collect=True, monitor=True
        )
    )
    files.append(
        File(
            name="surf_out",
            evaluation_path="surf*.out",
            type="text/plain",
            collect=True,
            monitor=True,
        )
    )
    files.append(
        File(
            name="vol_out",
            evaluation_path="vol*.out",
            type="text/plain",
            collect=True,
            monitor=True,
        )
    )
    files.append(
        File(
            name="err", evaluation_path="*error.log", type="text/plain", collect=True, monitor=True
        )
    )
    files.append(
        File(
            name="output_cas",
            evaluation_path="nozzle.cas.h5",
            type="application/octet-stream",
            collect=True,
            monitor=False,
        )
    )
    files.append(
        File(
            name="output_data",
            evaluation_path="nozzle.dat.h5",
            type="application/octet-stream",
            collect=True,
            monitor=False,
        )
    )

    files = project_api.create_files(files)
    file_ids = {f.name: f.id for f in files}

    log.debug("=== JobDefinition with simulation workflow and parameters")
    job_def = JobDefinition(name="JobDefinition.1", active=True)

    exec_script_file = project_api.copy_default_execution_script(
        f"fluent-v{version[2:4]}{version[6]}-exec_fluent.py"
    )

    # Task definition
    num_input_files = 2
    task_def = TaskDefinition(
        name="Fluent Run",
        software_requirements=[
            Software(name="Ansys Fluent", version=version),
        ],
        execution_command=None,  # Only execution currently supported
        use_execution_script=True,
        execution_script_id=exec_script_file.id,
        resource_requirements=ResourceRequirements(
            num_cores=4,
            distributed=True,
        ),
        execution_level=0,
        execution_context={
            "dimension": "3d",
            "double_precision": True,
            "mode": "solution",
        },
        max_execution_time=120.0,
        num_trials=1,
        input_file_ids=[f.id for f in files[:num_input_files]],
        output_file_ids=[f.id for f in files[num_input_files:]],
        success_criteria=SuccessCriteria(
            return_code=0,
            required_output_file_ids=[
                file_ids["output_cas"],
                file_ids["surf_out"],
                file_ids["vol_out"],
            ],
            require_all_output_files=False,
        ),
    )

    task_defs = [task_def]
    task_defs = project_api.create_task_definitions(task_defs)

    job_def.task_definition_ids = [td.id for td in task_defs]

    # Create job_definition in project
    job_def = project_api.create_job_definitions([job_def])[0]

    job_def = project_api.get_job_definitions()[0]

    log.debug(f"=== Create {num_jobs} jobs")
    jobs = []
    for i in range(num_jobs):
        jobs.append(Job(name=f"Job.{i}", eval_status="pending", job_definition_id=job_def.id))
    jobs = project_api.create_jobs(jobs)

    log.info(f"Created project '{proj.name}', ID='{proj.id}'")
    return proj


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, default="Fluent nozzle")
    parser.add_argument("-j", "--num-jobs", type=int, default=1)
    parser.add_argument("-U", "--url", default="https://127.0.0.1:8443/hps")
    parser.add_argument("-u", "--username", default="repuser")
    parser.add_argument("-p", "--password", default="repuser")
    parser.add_argument("-t", "--token", default=None)
    parser.add_argument("-v", "--ansys-version", default=__ansys_apps_version__)
    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    try:
        log.info("Connect to HPC Platform Services")
        if args.token:
            client = Client(url=args.url, token=args.token)
        else:
            client = Client(url=args.url, username=args.username, password=args.password)
        log.info(f"HPS URL: {client.url}")
        proj = create_project(
            client=client, name=args.name, num_jobs=args.num_jobs, version=args.ansys_version
        )

    except HPSError as e:
        log.error(str(e))
