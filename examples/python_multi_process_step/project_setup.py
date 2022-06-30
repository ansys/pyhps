# ----------------------------------------------------------
# Copyright (C) 2021 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): R.Walker
# ----------------------------------------------------------
'''
Project setup script for multi process step and task file replacement testing.

Run *python eval.py --help* for command line arguments.

The project id is generated as 
"py_{NUM_PROCESS_STEPS}_ps" and the `_img` is appended if result image is written.

Per default the project is inactive. You can activate the project with the `-a` flag


Example:
```
python project_setup.py -n 100 -c 10 --no-images
```
Create 100 design points 
  and change the first 10 design points 
  and do not write an result image.



'''
import argparse
import logging
import os
import random
import sys

from ansys.rep.client import DCSError
from ansys.rep.client.jms import (Client, File, FitnessDefinition,
                                  IntParameterDefinition, Job, JobDefinition,
                                  ParameterMapping, Project,
                                  ResourceRequirements, Software,
                                  StringParameterDefinition, SuccessCriteria,
                                  TaskDefinition)

from task_files import update_task_files

log = logging.getLogger(__name__)


def main(client, num_task_definitions, num_jobs, duration, period, images, change_job_tasks, inactive, sequential):
    """
    Python project implementing multiple process steps and optional image generation
    """
    log.debug("=== Project")
    proj = Project(
        name=f"py_{num_task_definitions}ps{'_img' if images else ''}{'_seq' if sequential else '_para'}",
        display_name=f"Python - {num_task_definitions} Task Defs {' - Img' if images else ''}{' - Sequential' if sequential else ' - Parallel'}",
        priority=1,
        active=not inactive)
    proj = client.create_project(proj, replace=True)

    log.debug("=== Files")

    cwd = os.path.dirname(__file__)

    files = []
    for i in range(num_task_definitions):
        # input
        files.append(File(name=f"td{i}_input",
                          evaluation_path=f"td{i}_input.json",
                          type="application/json",
                          src=os.path.join(cwd, "input.json")))
        # eval script
        files.append(File(name=f"td{i}_pyscript",
                          evaluation_path="eval.py",
                          type="text/plain",
                          src=os.path.join(cwd, "eval.py")))
        # output text
        files.append(File(name=f"td{i}_results",
                          evaluation_path=f"td{i}_results.txt",
                          collect=True, monitor=True,
                          type="text/plain"))
        # output json
        files.append(File(name=f"td{i}_results_json",
                          evaluation_path=f"td{i}_results.json",
                          collect=True, monitor=False,
                          type="application/json"))
        # output image
        if images:
            files.append(File(name=f"td{i}_results_jpg",
                              evaluation_path=f"td{i}_results.jpg",
                              type="image/jpeg", collect=True))

    files = proj.create_files(files)
    file_ids = {f.name: f.id for f in files}

    log.debug("=== JobDefinition with simulation workflow and parameters")
    job_def = JobDefinition(name="job_definition.1", active=True)

    log.debug("=== Parameters")
    params = []
    mappings = []
    for i in range(num_task_definitions):
        int_params = [
            IntParameterDefinition(name=f'period{i}', lower_limit=1, upper_limit=period, units="s"),
            IntParameterDefinition(name=f'duration{i}', lower_limit=0, upper_limit=duration, units="s"),
            IntParameterDefinition(name=f"steps{i}", units=""),
        ]
        str_params = [
            StringParameterDefinition(name=f'color{i}', value_list=['red', 'blue', 'green', 'yellow', 'cyan'], default='"orange"'),
        ]
        int_params = proj.create_parameter_definitions(int_params)
        str_params = proj.create_parameter_definitions(str_params)
        params.extend(int_params+str_params)

        input_file_id = file_ids[f"td{i}_input"]
        result_file_id = file_ids[f"td{i}_results_json"]

        mappings.append(ParameterMapping(key_string='"period"', tokenizer=":", parameter_definition_id=int_params[0].id, file_id=input_file_id))
        mappings.append(ParameterMapping(key_string='"duration"', tokenizer=":",
                                   parameter_definition_id=int_params[1].id, file_id=input_file_id))
        mappings.append(ParameterMapping(key_string='"steps"', tokenizer=":",
                                   parameter_definition_id=int_params[2].id, file_id=result_file_id))
        mappings.append(ParameterMapping(key_string='"color"', tokenizer=":", string_quote='"',
                                   parameter_definition_id=str_params[0].id, file_id=input_file_id))

    mappings = proj.create_parameter_mappings(mappings)

    log.debug("=== Task definitions")
    task_defs = []
    for i in range(num_task_definitions):
        input_file_ids = [file_ids[f"td{i}_input"], file_ids[f"td{i}_pyscript"]]
        output_file_ids = [file_ids[f"td{i}_results"], file_ids[f"td{i}_results_json"]]
        if f"td{i}_results_jpg" in file_ids.keys():
            output_file_ids.append(file_ids[f"td{i}_results_jpg"])

        cmd = f'%executable% %file:td{i}_pyscript% %file:td{i}_input% {i}'
        if images:
            cmd += ' --images'
        task_defs.append(TaskDefinition(
            name=f"td{i}_py_eval",
            software_requirements = [
                Software(name="Python", version="3.10"),
            ],
            execution_command=cmd,
            max_execution_time=duration*1.5,
            resource_requirements=ResourceRequirements(
                cpu_core_usage=0.2,
                memory=100,
                disk_space=1,
            ),
            execution_level=i if sequential else 0,
            input_file_ids=input_file_ids,
            output_file_ids=output_file_ids,
            store_output=True,
            success_criteria=SuccessCriteria(
                return_code=0, require_all_output_files=True)
        ))

    task_defs = proj.create_task_definitions(task_defs)

    # Create job_definition in project
    job_def.parameter_definition_ids = [o.id for o in params]
    job_def.parameter_mapping_ids = [o.id for o in mappings]
    job_def.task_definition_ids = [o.id for o in task_defs]
    job_def = proj.create_job_definitions([job_def])[0]

    # Refresh param definitions
    params = proj.get_parameter_definitions(id=job_def.parameter_definition_ids)

    log.debug("=== Design points")
    jobs = []
    for i in range(num_jobs):
        values = {}
        for p in params:
            if p.mode == 'input':
                if p.type == 'string':
                    values[p.name] = random.choice(p.value_list)
                elif p.type == "int":
                    values[p.name] = int(
                        p.lower_limit + random.random()*(p.upper_limit-p.lower_limit))
        jobs.append(Job(
            name=f"Job.{i}", values=values, eval_status="pending"))
    jobs = job_def.create_jobs(jobs)

    # change dp task files
    if change_job_tasks > 0:
        log.info(f'Change tasks for {change_job_tasks} jobs')
        update_task_files(proj, change_job_tasks, images)

    log.info(f"Created project '{proj.name}', ID='{proj.id}'")


if __name__ == "__main__":

    logger = logging.getLogger()
    logging.basicConfig(
        format='[%(asctime)s | %(levelname)s] %(message)s', level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('-U', '--url', default="https://127.0.0.1:8443/rep")
    parser.add_argument('-u', '--username', default="repadmin")
    parser.add_argument('-p', '--password', default="repadmin")
    parser.add_argument('-n', '--num-jobs', type=int, default=10)
    parser.add_argument('-t', '--num-task-definitions', type=int, default=3)
    parser.add_argument('-d', '--duration', type=int, default=10)
    parser.add_argument('-e', '--period', type=int, default=3)
    parser.add_argument('-c', '--change-job-tasks', type=int, default=0,
                        help='Change task files of how many design points')
    parser.add_argument('--inactive',  action='store_true',
                        default=False, help='Set project to inactive')
    parser.add_argument('--images', action='store_true',
                        default=False, help="Enable if you want images to be generated. Needs PIL installed ( `pip install pillow` ) ")
    parser.add_argument('--sequential', action='store_true', default=False,
                        help="Whether to evaluate all process steps of a design point sequentially or in parallel (same execution level)")

    args = parser.parse_args()

    log.debug("=== DCS connection")
    client = Client(rep_url=args.url, username=args.username, password=args.password)

    try:
        main(client,
        num_task_definitions=args.num_task_definitions, 
        num_jobs=args.num_jobs, 
        duration=args.duration, 
        period=args.period, 
        images=args.images, 
        change_job_tasks=args.change_job_tasks, 
        inactive=args.inactive, 
        sequential=args.sequential,
        )
    except DCSError as e:
        log.error(str(e))
