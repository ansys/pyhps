"""
Script showing how to submit an LS-DYNA job to Ansys HPC Platform Services.

Once submitted, minimal job information are serialized to a JSON file rep_job.json.
This mimics what an application would need to store in order to
subsequently monitor the job and download results.

The job consists of two tasks:
 - The first task runs the actual LS-DYNA simulation
 - The second task runs a little LS-PrePost script to
   post-process the results of the first task.

Usage:

    $ python lsdyna_job.py submit
    $ python lsdyna_job.py monitor
    $ python lsdyna_job.py download
"""

import argparse
import logging
import os
import random

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

USE_LSDYNA_MPP = False


def create_project(
    client, name, version=__ansys_apps_version__, num_jobs=20, use_exec_script=False, active=True
) -> Project:
    """Create a REP project running a simple LS-DYNA
    job simulating the impact of a cylinder made of Aluminum
    against a plate made of steel.
    """

    log.info("=== Connect to the REP server")
    jms_api = JmsApi(client)

    log.info("=== Create an empty project")
    proj = Project(name=name, priority=1, active=True)
    proj = jms_api.create_project(proj)

    project_api = ProjectApi(client, proj.id)

    log.info("=== Create file resources")
    cwd = os.path.dirname(__file__)
    files = []

    # input files
    files.append(
        File(
            name="inp",
            evaluation_path="cylinder_plate.k",
            type="text/plain",
            src=os.path.join(cwd, "cylinder_plate.k"),
        )
    )
    files.append(
        File(
            name="post_commands",
            evaluation_path="postprocess.cfile",
            type="text/plain",
            src=os.path.join(cwd, "postprocess.cfile"),
        )
    )

    # output files
    files.append(
        File(name="d3hsp", evaluation_path="d3hsp", type="text/plain", collect=True, monitor=False)
    )
    if USE_LSDYNA_MPP:
        files.append(
            File(
                name="messag",
                evaluation_path="mes0000",
                type="text/plain",
                collect=True,
                monitor=True,
            )
        )  # for distributed run
    else:
        files.append(
            File(
                name="messag",
                evaluation_path="messag",
                type="text/plain",
                collect=True,
                monitor=True,
            )
        )  # for shared memory run
    files.append(
        File(
            name="d3plot",
            evaluation_path="d3plot*",
            type="application/octet-stream",
            collect=True,
            monitor=False,
        )
    )
    files.append(
        File(name="img", evaluation_path="**.png", type="image/png", collect=True, monitor=False)
    )
    files.append(
        File(
            name="movie",
            evaluation_path="**.wmv",
            type="video/x-ms-wmv",
            collect=True,
            monitor=False,
        )
    )

    files = project_api.create_files(files)
    file_ids = {f.name: f.id for f in files}

    log.info("=== Simulation workflow")
    job_def = JobDefinition(name="JobDefinition.1", active=True)

    # Define process steps (task definitions)
    ls_dyna_command = "%executable% i=%file:inp% ncpu=%resource:num_cores% memory=300m"
    if USE_LSDYNA_MPP:
        ls_dyna_command = "%executable% -dis -np %resource:num_cores% i=%file:inp% memory=300m"

    task_defs = []
    task_def1 = TaskDefinition(
        name="LS-DYNA Run",
        software_requirements=[Software(name="Ansys LS-DYNA", version=version)],
        execution_command=ls_dyna_command,
        max_execution_time=3600.0,
        resource_requirements=ResourceRequirements(
            num_cores=6,
            memory=6000 * 1024 * 1024,
            disk_space=4000 * 1024 * 1024,
            distributed=USE_LSDYNA_MPP,
        ),
        execution_level=0,
        num_trials=1,
        input_file_ids=[file_ids["inp"]],
        output_file_ids=[file_ids["d3hsp"], file_ids["messag"], file_ids["d3plot"]],
        success_criteria=SuccessCriteria(
            return_code=0,
            required_output_file_ids=[file_ids["d3plot"]],
            require_all_output_parameters=False,
            require_all_output_files=False,
        ),
    )

    if use_exec_script:
        exec_script_file = project_api.copy_default_execution_script(
            f"lsdyna-v{version[2:4]}{version[6]}-exec_lsdyna.py"
        )

        task_def1.use_execution_script = True
        task_def1.execution_script_id = exec_script_file.id

    task_defs.append(task_def1)

    task_def2 = TaskDefinition(
        name="LS-PrePost Run",
        software_requirements=[Software(name="Ansys LS-PrePost", version=version)],
        execution_command="%executable% c=%file:post_commands%",
        max_execution_time=600.0,
        resource_requirements=ResourceRequirements(
            num_cores=2,
            memory=3000,
            disk_space=4000,
            distributed=False,
            platform="Windows",
        ),
        execution_level=1,
        num_trials=1,
        input_file_ids=[file_ids["post_commands"], file_ids["d3plot"]],
        output_file_ids=[file_ids["img"], file_ids["movie"]],
        success_criteria=SuccessCriteria(
            required_output_file_ids=[file_ids["movie"]],
            require_all_output_parameters=False,
            require_all_output_files=False,
        ),
    )

    task_defs.append(task_def2)

    task_definitions = project_api.create_task_definitions(task_defs)

    # Create job definition in project
    job_def = JobDefinition(name="JobDefinition.1", active=True)
    job_def.task_definition_ids = [td.id for td in task_definitions]

    job_def = project_api.create_job_definitions([job_def])[0]

    # Refresh the parameters
    params = project_api.get_parameter_definitions(id=job_def.parameter_definition_ids)

    log.debug("=== Jobs")
    jobs = []
    for i in range(num_jobs):
        values = {
            p.name: p.lower_limit + random.random() * (p.upper_limit - p.lower_limit)
            for p in params
            if p.mode == "input"
        }
        jobs.append(
            Job(name=f"Job.{i}", values=values, eval_status="pending", job_definition_id=job_def.id)
        )
    jobs = project_api.create_jobs(jobs)

    log.info(f"Created project '{proj.name}', ID='{proj.id}'")

    return proj


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, default="LS-DYNA Cylinder Plate")
    parser.add_argument("-j", "--num-jobs", type=int, default=10)
    parser.add_argument("-es", "--use-exec-script", default=False, type=bool)
    parser.add_argument("-U", "--url", default="https://localhost:8443/rep")
    parser.add_argument("-u", "--username", default="repadmin")
    parser.add_argument("-p", "--password", default="repadmin")
    parser.add_argument("-v", "--ansys-version", default=__ansys_apps_version__)

    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.DEBUG)

    log.debug("=== HPS connection")
    client = Client(rep_url=args.url, username=args.username, password=args.password)

    try:
        log.info(f"HPS URL: {client.rep_url}")
        proj = create_project(
            client=client,
            name=args.name,
            version=args.ansys_version,
            num_jobs=args.num_jobs,
            use_exec_script=args.use_exec_script,
        )
    except HPSError as e:
        log.error(str(e))
