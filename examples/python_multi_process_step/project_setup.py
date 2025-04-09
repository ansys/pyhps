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

"""Project set up script for multi-steps (task definitions) and task file replacement testing.

Author(s): R.Walker

Run *python project_setup.py --help* for command line arguments.

The project id is generated as
"Python - {NUM_PROCESS_STEPS} Task Defs (- Img )- Sequential/Parallel"


Example:
-------
```
python project_setup.py -n 100 -c 10
```
Create 100 design points with the default 3 tasks each
  and change the first 10 design points
  and do not write a result image.

"""

import argparse
import logging
import os
import random

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
    StringParameterDefinition,
    SuccessCriteria,
    TaskDefinition,
)

from .task_files import update_task_files

log = logging.getLogger(__name__)


def main(
    client,
    num_task_definitions,
    num_jobs,
    duration,
    period,
    images,
    change_job_tasks,
    inactive,
    sequential,
    python_version=None,
) -> Project:
    """Python project implementing multiple steps and optional image generation."""
    log.debug("=== Project")
    name = f"Python - {num_task_definitions} Task Defs {' - Img' if images else ''}"
    name += f"{' - Sequential' if sequential else ' - Parallel'}"
    proj = Project(
        name=name,
        priority=1,
        active=not inactive,
    )
    jms_api = JmsApi(client)
    proj = jms_api.create_project(proj, replace=True)
    project_api = ProjectApi(client, proj.id)

    log.debug("=== Files")

    cwd = os.path.dirname(__file__)

    files = []
    for i in range(num_task_definitions):
        # input
        files.append(
            File(
                name=f"td{i}_input",
                evaluation_path=f"td{i}_input.json",
                type="application/json",
                src=os.path.join(cwd, "input.json"),
            )
        )
        # eval script
        files.append(
            File(
                name=f"td{i}_pyscript",
                evaluation_path="eval.py",
                type="text/plain",
                src=os.path.join(cwd, "eval.py"),
            )
        )
        # output text
        files.append(
            File(
                name=f"td{i}_results",
                evaluation_path=f"td{i}_results.txt",
                collect=True,
                monitor=True,
                type="text/plain",
            )
        )
        # output json
        files.append(
            File(
                name=f"td{i}_results_json",
                evaluation_path=f"td{i}_results.json",
                collect=True,
                monitor=False,
                type="application/json",
            )
        )
        # output image
        if images:
            files.append(
                File(
                    name=f"td{i}_results_jpg",
                    evaluation_path=f"td{i}_results.jpg",
                    type="image/jpeg",
                    collect=True,
                )
            )

    files = project_api.create_files(files)
    file_ids = {f.name: f.id for f in files}

    log.debug("=== JobDefinition with simulation workflow and parameters")
    job_def = JobDefinition(name="job_definition.1", active=True)

    log.debug("=== Parameters")
    params = []
    mappings = []
    for i in range(num_task_definitions):
        new_params = [
            IntParameterDefinition(
                name=f"period{i}", lower_limit=1, upper_limit=period, units="s", mode="input"
            ),
            IntParameterDefinition(
                name=f"duration{i}", lower_limit=0, upper_limit=duration, units="s", mode="input"
            ),
            IntParameterDefinition(name=f"steps{i}", units="", mode="output"),
            StringParameterDefinition(
                name=f"color{i}",
                value_list=["red", "blue", "green", "yellow", "cyan"],
                default='"orange"',
                mode="input",
            ),
        ]
        new_params = project_api.create_parameter_definitions(new_params)
        params.extend(new_params)

        input_file_id = file_ids[f"td{i}_input"]
        result_file_id = file_ids[f"td{i}_results_json"]

        mappings.append(
            ParameterMapping(
                key_string='"period"',
                tokenizer=":",
                parameter_definition_id=new_params[0].id,
                file_id=input_file_id,
            )
        )
        mappings.append(
            ParameterMapping(
                key_string='"duration"',
                tokenizer=":",
                parameter_definition_id=new_params[1].id,
                file_id=input_file_id,
            )
        )
        mappings.append(
            ParameterMapping(
                key_string='"steps"',
                tokenizer=":",
                parameter_definition_id=new_params[2].id,
                file_id=result_file_id,
            )
        )
        mappings.append(
            ParameterMapping(
                key_string='"color"',
                tokenizer=":",
                string_quote='"',
                parameter_definition_id=new_params[3].id,
                file_id=input_file_id,
            )
        )

    mappings = project_api.create_parameter_mappings(mappings)

    log.debug("=== Task definitions")
    task_defs = []
    for i in range(num_task_definitions):
        input_file_ids = [file_ids[f"td{i}_input"], file_ids[f"td{i}_pyscript"]]
        output_file_ids = [file_ids[f"td{i}_results"], file_ids[f"td{i}_results_json"]]
        if f"td{i}_results_jpg" in file_ids.keys():
            output_file_ids.append(file_ids[f"td{i}_results_jpg"])

        cmd = f"%executable% %file:td{i}_pyscript% %file:td{i}_input% {i}"
        if images:
            cmd += " --images"
        task_defs.append(
            TaskDefinition(
                name=f"td{i}_py_eval",
                software_requirements=[
                    Software(name="Python", version=python_version),
                ],
                execution_command=cmd,
                max_execution_time=duration * 1.5 + 12.0,
                resource_requirements=ResourceRequirements(
                    num_cores=0.2,
                    memory=100 * 1024 * 1024,  # 100 MB
                    disk_space=1 * 1024 * 1024,  # 1 MB
                ),
                execution_level=i if sequential else 0,
                input_file_ids=input_file_ids,
                output_file_ids=output_file_ids,
                store_output=True,
                success_criteria=SuccessCriteria(return_code=0, require_all_output_files=True),
            )
        )

    task_defs = project_api.create_task_definitions(task_defs)

    # Create job_definition in project
    job_def.parameter_definition_ids = [o.id for o in params]
    job_def.parameter_mapping_ids = [o.id for o in mappings]
    job_def.task_definition_ids = [o.id for o in task_defs]
    job_def = project_api.create_job_definitions([job_def])[0]

    # Refresh param definitions
    params = project_api.get_parameter_definitions(id=job_def.parameter_definition_ids)

    log.debug("=== Design points")
    jobs = []
    for i in range(num_jobs):
        values = {}
        for p in params:
            if p.mode == "input":
                if p.type == "string":
                    values[p.name] = random.choice(p.value_list)
                elif p.type == "int":
                    values[p.name] = int(
                        p.lower_limit + random.random() * (p.upper_limit - p.lower_limit)
                    )
        jobs.append(
            Job(name=f"Job.{i}", values=values, eval_status="pending", job_definition_id=job_def.id)
        )
    jobs = project_api.create_jobs(jobs)

    # change dp task files
    if change_job_tasks > 0:
        log.info(f"Change tasks for {change_job_tasks} jobs")
        update_task_files(project_api, change_job_tasks, images)

    log.info(f"Created project '{proj.name}', ID='{proj.id}'")

    return proj


if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("-U", "--url", default="https://127.0.0.1:8443/hps")
    parser.add_argument("-u", "--username", default="repuser")
    parser.add_argument("-p", "--password", default="repuser")
    parser.add_argument("-t", "--token", default=None)
    parser.add_argument("-n", "--num-jobs", type=int, default=10)
    parser.add_argument("-td", "--num-task-definitions", type=int, default=3)
    parser.add_argument("-d", "--duration", type=int, default=10)
    parser.add_argument("-e", "--period", type=int, default=3)
    parser.add_argument(
        "-c",
        "--change-job-tasks",
        type=int,
        default=0,
        help="Change task files of how many design points",
    )
    parser.add_argument(
        "--inactive", action="store_true", default=False, help="Set project to inactive"
    )
    parser.add_argument(
        "--images",
        action="store_true",
        default=False,
        help="Enable if you want images generated. Needs PIL installed ( `pip install pillow` ) ",
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        default=False,
        help="Whether to evaluate all tasks of same exec level per job sequentially or in parallel",
    )
    parser.add_argument("-v", "--python-version", default="3.10")

    args = parser.parse_args()

    log.debug("=== HPS connection")
    if args.token:
        client = Client(url=args.url, token=args.token)
    else:
        client = Client(url=args.url, username=args.username, password=args.password)

    try:
        main(
            client,
            num_task_definitions=args.num_task_definitions,
            num_jobs=args.num_jobs,
            duration=args.duration,
            period=args.period,
            images=args.images,
            change_job_tasks=args.change_job_tasks,
            inactive=args.inactive,
            sequential=args.sequential,
            python_version=args.python_version,
        )
    except HPSError as e:
        log.error(str(e))
