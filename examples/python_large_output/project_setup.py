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
Python job that can create large output files
"""

import argparse
import logging
import os

from ansys.hps.client import Client, HPSError
from ansys.hps.client.jms import (
    File,
    IntParameterDefinition,
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


def main(client, use_exec_script, python_version=None) -> Project:
    """
    Create project that runs a Python script to generate a large output file.
    """
    log.debug("=== Project")
    proj = Project(name="Python Large Output Files", priority=1, active=True)
    jms_api = JmsApi(client)
    proj = jms_api.create_project(proj, replace=True)
    project_api = ProjectApi(client, proj.id)

    log.debug("=== Files")
    cwd = os.path.dirname(__file__)

    files = [
        File(
            name="script",
            evaluation_path="evaluate.py",
            type="text/plain",
            src=os.path.join(cwd, "evaluate.py"),
        ),
        File(
            name="output",
            evaluation_path="output.bin",
            type="application/octet-stream",
            monitor=False,
            collect=True,
        ),
    ]

    if use_exec_script:
        # Define and upload an exemplary exec script to run Python
        files.append(
            File(
                name="exec_python",
                evaluation_path="exec_python.py",
                type="application/x-python-code",
                src=os.path.join(cwd, "exec_python.py"),
            )
        )

    files = project_api.create_files(files)
    file_ids = {f.name: f.id for f in files}

    log.debug("=== Job Definition with simulation workflow and parameters")
    job_def = JobDefinition(name="JobDefinition.1", active=True)

    # Input params
    input_params = [
        IntParameterDefinition(
            name="size", lower_limit=1, upper_limit=1000, default=1, mode="input"
        ),
    ]
    input_params = project_api.create_parameter_definitions(input_params)

    mappings = [
        ParameterMapping(
            key_string="size",
            tokenizer="=",
            parameter_definition_id=input_params[0].id,
            file_id=file_ids["script"],
        ),
    ]

    output_params = []
    # output_params = project_api.create_parameter_definitions(output_params)
    # mappings.extend([])

    mappings = project_api.create_parameter_mappings(mappings)

    job_def.parameter_definition_ids = [o.id for o in input_params + output_params]
    job_def.parameter_mapping_ids = [o.id for o in mappings]

    task_def = TaskDefinition(
        name="Python",
        software_requirements=[Software(name="Python", version=python_version)],
        execution_command="%executable% %file:script%",
        resource_requirements=ResourceRequirements(num_cores=0.5),
        execution_level=0,
        input_file_ids=[file_ids["script"]],
        output_file_ids=[file_ids["output"]],
    )

    if use_exec_script:
        task_def.use_execution_script = True
        task_def.execution_script_id = file_ids["exec_python"]

    task_def = project_api.create_task_definitions([task_def])[0]
    job_def.task_definition_ids = [task_def.id]

    # Create job_definition in project
    job_def = project_api.create_job_definitions([job_def])[0]

    params = project_api.get_parameter_definitions(job_def.parameter_definition_ids)

    log.debug("=== Jobs")
    jobs = []

    for size in [1, 5]:
        jobs.append(
            Job(
                name=f"Job {size} GB",
                values={"size": size},
                eval_status="pending",
                job_definition_id=job_def.id,
            )
        )
    for size in [10, 25, 50, 100, 250]:
        jobs.append(
            Job(
                name=f"Job {size} GB",
                values={"size": size},
                eval_status="inactive",
                job_definition_id=job_def.id,
            )
        )

    jobs = project_api.create_jobs(jobs)

    log.info(f"Created project '{proj.name}', ID='{proj.id}'")

    return proj


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-U", "--url", default="https://127.0.0.1:8443/hps")
    parser.add_argument("-u", "--username", default="repuser")
    parser.add_argument("-p", "--password", default="repuser")
    parser.add_argument("-es", "--use-exec-script", default=False, action="store_true")
    parser.add_argument("-v", "--python-version", default="3.10")
    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.DEBUG)

    client = Client(url=args.url, username=args.username, password=args.password)

    try:
        main(client, use_exec_script=args.use_exec_script, python_version=args.python_version)
    except HPSError as e:
        log.error(str(e))
