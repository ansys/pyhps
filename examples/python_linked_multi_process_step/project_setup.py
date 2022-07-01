# ----------------------------------------------------------
# Copyright (C) 2021 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): R.Walker
# ----------------------------------------------------------

import argparse
import logging
import os
import random
import sys

from ansys.rep.client import REPError
from ansys.rep.client.jms import (
    Client,
    File,
    FitnessDefinition,
    FloatParameterDefinition,
    Job,
    JobDefinition,
    ParameterMapping,
    Project,
    ResourceRequirements,
    Software,
    SuccessCriteria,
    TaskDefinition,
)

log = logging.getLogger(__name__)


def main(client, num_task_definitions, num_jobs, start, inactive):
    """Python project implementing multiple process steps and linkage of files between process steps"""

    log.debug("=== Project")
    proj = Project(
        name=f"py_linked_{num_task_definitions}td",
        display_name=f"Python - Linked Files - {num_task_definitions} Process Steps",
        priority=1,
        active=not inactive,
    )
    proj = client.create_project(proj, replace=True)

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

    files = proj.create_files(files)
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
    params = proj.create_parameter_definitions(params)
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
    param_mappings = proj.create_parameter_mappings(param_mappings)
    job_def.parameter_mapping_ids = [o.id for o in param_mappings]

    log.debug("=== Process Steps")
    task_defs = []
    for i in range(num_task_definitions):

        input_file_ids = [file_ids[f"td{i}_pyscript"]]
        if i == 0:
            input_file_ids.append(file_ids["input"])
            cmd = f"%executable% %file:td{i}_pyscript% %file:input% {i}"
        else:
            input_file_ids.append(file_ids[f"td{i-1}_result"])
            cmd = f"%executable% %file:td{i}_pyscript% %file:td{i-1}_result% {i}"

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
                    cpu_core_usage=0.2,
                    memory=100,
                    disk_space=1,
                ),
                input_file_ids=input_file_ids,
                output_file_ids=output_file_ids,
                store_output=True,
                success_criteria=SuccessCriteria(return_code=0, require_all_output_files=True),
            )
        )
    task_defs = proj.create_task_definitions(task_defs)
    job_def.task_definition_ids = [o.id for o in task_defs]

    # Create job_definition in project
    job_def = proj.create_job_definitions([job_def])[0]

    # Refresh parameter definitions
    params = proj.get_parameter_definitions(job_def.parameter_definition_ids)

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
        jobs.append(Job(name=f"Job.{i}", values=values, eval_status="pending"))
    jobs = job_def.create_jobs(jobs)

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

    log.debug("=== DCS connection")
    client = Client(rep_url=args.url, username=args.username, password=args.password)
    try:
        main(
            client,
            num_jobs=args.num_jobs,
            num_task_definitions=args.num_task_definitions,
            start=args.start,
            inactive=args.inactive,
        )
    except REPError as e:
        log.error(str(e))
