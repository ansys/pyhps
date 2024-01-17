# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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
Python example with multiple dependent tasks and linked files in between.

Author(s): R.Walker
"""
import argparse
import logging
import os
import random

from ansys.hps.client import Client, HPSError
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
    SuccessCriteria,
    TaskDefinition,
)

log = logging.getLogger(__name__)


def main(client, num_task_definitions, num_jobs, start, inactive):
    """Create project with multiple dependent Python tasks and linked files in between."""
    log.debug("=== Project")
    proj = Project(
        name=f"Python - Linked Files - {num_task_definitions} Tasks",
        priority=1,
        active=not inactive,
    )
    jms_api = JmsApi(client)
    proj = jms_api.create_project(proj, replace=True)
    project_api = ProjectApi(client, proj.id)

    log.debug("=== Files")
    cwd = os.path.dirname(__file__)
    files = []
    # Start input file for first process step
    files.append(
        File(
            name="input",
            evaluation_path="input.json",
            type="application/json",
            src=os.path.join(cwd, "input.json"),
        )
    )

    for i in range(num_task_definitions):
        files.append(
            File(
                name=f"td{i}_pyscript",
                evaluation_path="eval.py",
                type="text/plain",
                src=os.path.join(cwd, "eval.py"),
            )
        )

        files.append(
            File(
                name=f"td{i}_result",
                evaluation_path=f"td{i}_result.json",
                collect=True,
                monitor=False,
                type="text/plain",
            )
        )

    files = project_api.create_files(files)
    file_ids = {f.name: f.id for f in files}

    log.debug("=== JobDefinition with simulation workflow and parameters")
    job_def = JobDefinition(name="job_definition.1", active=True)

    log.debug("=== Parameters")
    params = [
        FloatParameterDefinition(name="start", lower_limit=1.0, upper_limit=start),
    ]
    params.extend(
        [FloatParameterDefinition(name=f"product{i}") for i in range(num_task_definitions)]
    )
    params = project_api.create_parameter_definitions(params)
    job_def.parameter_definition_ids = [o.id for o in params]

    param_mappings = [
        ParameterMapping(
            key_string='"start"',
            tokenizer=":",
            parameter_definition_id=params[0].id,
            file_id=file_ids["input"],
        )
    ]
    param_mappings.extend(
        [
            ParameterMapping(
                key_string='"product"',
                tokenizer=":",
                parameter_definition_id=params[i + 1].id,
                file_id=file_ids[f"td{i}_result"],
            )
            for i in range(num_task_definitions)
        ]
    )
    param_mappings = project_api.create_parameter_mappings(param_mappings)
    job_def.parameter_mapping_ids = [o.id for o in param_mappings]

    log.debug("=== Process Steps")
    task_defs = []
    for i in range(num_task_definitions):

        input_file_ids = [file_ids[f"td{i}_pyscript"]]
        if i == 0:
            input_file_ids.append(file_ids["input"])
            cmd = f"%executable% %file:td{i}_pyscript% %file:input% {i}"  # noqa: E231
        else:
            input_file_ids.append(file_ids[f"td{i-1}_result"])
            cmd = f"%executable% %file:td{i}_pyscript% %file:td{i-1}_result% {i}"  # noqa: E231

        output_file_ids = [file_ids[f"td{i}_result"]]

        task_defs.append(
            TaskDefinition(
                name=f"td{i}_py_eval",
                software_requirements=[
                    Software(
                        name="Python",
                        version="3.10",
                    )
                ],
                execution_command=cmd,
                max_execution_time=10,
                execution_level=i,
                resource_requirements=ResourceRequirements(
                    num_cores=0.2,
                    memory=100 * 1024 * 1024,  # 100 MB
                    disk_space=1 * 1024 * 1024,  # 1 MB
                ),
                input_file_ids=input_file_ids,
                output_file_ids=output_file_ids,
                store_output=True,
                success_criteria=SuccessCriteria(return_code=0, require_all_output_files=True),
            )
        )
    task_defs = project_api.create_task_definitions(task_defs)
    job_def.task_definition_ids = [o.id for o in task_defs]

    # Create job_definition in project
    job_def = project_api.create_job_definitions([job_def])[0]

    # Refresh parameter definitions
    params = project_api.get_parameter_definitions(job_def.parameter_definition_ids)

    log.debug("=== Design points")
    jobs = []
    for i in range(num_jobs):
        values = {}
        for p in params:
            if p.mode == "input":
                if p.type == "float":
                    values[p.name] = float(
                        int(p.lower_limit + random.random() * (p.upper_limit - p.lower_limit))
                    )
        jobs.append(
            Job(name=f"Job.{i}", values=values, eval_status="pending", job_definition_id=job_def.id)
        )
    jobs = project_api.create_jobs(jobs)

    log.info(f"Created project '{proj.name}', ID='{proj.id}'")


if __name__ == "__main__":

    logger = logging.getLogger()
    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("-U", "--url", default="https://127.0.0.1:8443/rep")
    parser.add_argument("-u", "--username", default="repadmin")
    parser.add_argument("-p", "--password", default="repadmin")
    parser.add_argument("-j", "--num-jobs", type=int, default=10)
    parser.add_argument("-t", "--num-task-definitions", type=int, default=3)
    parser.add_argument("-f", "--start", type=float, default=10.0)
    parser.add_argument(
        "-i", "--inactive", action="store_true", default=False, help="Set project to inactive"
    )

    args = parser.parse_args()

    log.debug("=== HPS connection")
    client = Client(url=args.url, username=args.username, password=args.password)
    try:
        main(
            client,
            num_jobs=args.num_jobs,
            num_task_definitions=args.num_task_definitions,
            start=args.start,
            inactive=args.inactive,
        )
    except HPSError as e:
        log.error(str(e))
