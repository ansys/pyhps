"""
Script showing how to submit an MAPDL linked analysis workflow (prestress-modal-harmonic)
as a multi-task job to REP.

The script shows two possible ways to submit the individual tasks:
    1. All-at-one: all 3 tasks are defined and included in the
       job definition before pushing it out to the server.
       When the job is created, it already has 3 tasks.

       $ python project_setup.py

    2. One-by-one: the first task is defined, pushed out to the server
       and then the job is created and submitted. Then, the second task is added
       to the job definition and the running job is synced to reflect the changes.
       The same for the third task.

       $ python project_setup.py --incremental

In both cases, output files from upstream tasks are used as input of downstream ones.
"""

import argparse
import logging
import os
from typing import List, Tuple

from ansys.hps.client import Client, REPError, __ansys_apps_version__
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

NUM_CORES = 2.0

log = logging.getLogger(__name__)


def create_prestress_task_definition(
    project_api: ProjectApi, use_exec_script: bool, version: str
) -> Tuple[str, List[File]]:

    log.info("=== Files")
    cwd = os.path.dirname(__file__)
    files = [
        File(
            name="inp",
            evaluation_path="prestres.dat",
            type="text/plain",
            src=os.path.join(cwd, "prestress.dat"),
        ),
        File(
            name="out", evaluation_path="solve.out", type="text/plain", collect=True, monitor=True
        ),
        File(
            name="rst",
            evaluation_path="file.rst",
            type="application/octet-stream",
            collect=True,
            monitor=False,
        ),
        File(
            name="err", evaluation_path="file*.err", type="text/plain", collect=True, monitor=True
        ),
        File(
            name="ldhi", evaluation_path="file.ldhi", type="text/plain", collect=True, monitor=False
        ),
        File(
            name="Rnn",
            evaluation_path="file*.r???",
            type="application/octet-stream",
            collect=True,
            monitor=False,
        ),
        File(
            name="rdb",
            evaluation_path="file.rdb",
            type="application/octet-stream",
            collect=True,
            monitor=False,
        ),
    ]

    files = project_api.create_files(files)
    file_ids = {f.name: f.id for f in files}

    task_defs = []
    task_def = TaskDefinition(
        name="Prestress",
        software_requirements=[Software(name="Ansys Mechanical APDL", version=version)],
        execution_command="%executable% -b -nolist -i %file:inp%"
        " -o solve.out -np %resource:num_cores%",
        max_execution_time=360.0,
        resource_requirements=ResourceRequirements(
            num_cores=NUM_CORES,
            distributed=True,
        ),
        execution_level=0,
        num_trials=1,
        input_file_ids=[file_ids["inp"]],
        output_file_ids=[id for name, id in file_ids.items() if name != "inp"],
    )

    if use_exec_script:
        exec_script_file = project_api.copy_default_execution_script(
            f"mapdl-v{version[2:4]}{version[6]}-exec_mapdl.py"
        )

        task_def.use_execution_script = True
        task_def.execution_script_id = exec_script_file.id

    task_defs.append(task_def)

    task_def = project_api.create_task_definitions(task_defs)[0]

    return task_def.id, [f for f in files if f.name in ["rst", "ldhi", "Rnn", "rdb"]]


def create_modal_task_definition(
    project_api: ProjectApi, prestress_files: List[File], use_exec_script: bool, version: str
) -> Tuple[str, List[File]]:

    log.info("=== Files")
    cwd = os.path.dirname(__file__)
    # the prestress output files already exist, no need to create them
    files = [
        File(
            name="inp",
            evaluation_path="modal.dat",
            type="text/plain",
            src=os.path.join(cwd, "modal.dat"),
        ),
        File(
            name="out", evaluation_path="solve.out", type="text/plain", collect=True, monitor=True
        ),
        File(
            name="rst",
            evaluation_path="file.rst",
            type="application/octet-stream",
            collect=True,
            monitor=False,
        ),
        File(
            name="err", evaluation_path="file*.err", type="text/plain", collect=True, monitor=True
        ),
        File(
            name="mode",
            evaluation_path="file*.mode",
            type="application/octet-stream",
            collect=True,
            monitor=False,
        ),
        File(
            name="db",
            evaluation_path="file.db",
            type="application/octet-stream",
            collect=True,
            monitor=False,
        ),
        File(
            name="esav",
            evaluation_path="file*.esav",
            type="application/octet-stream",
            collect=True,
            monitor=False,
        ),
        File(
            name="emat",
            evaluation_path="file*.emat",
            type="application/octet-stream",
            collect=True,
            monitor=False,
        ),
    ]

    files = project_api.create_files(files)
    file_ids = {f.name: f.id for f in files}

    # Process step
    input_file_ids = [file_ids["inp"]]
    input_file_ids.extend([f.id for f in prestress_files])

    task_defs = []
    task_def = TaskDefinition(
        name="Modal",
        software_requirements=[Software(name="Ansys Mechanical APDL", version=version)],
        execution_command="%executable% -b -nolist -i %file:inp% "
        "-o solve.out -np %resource:num_cores%",
        max_execution_time=360.0,
        resource_requirements=ResourceRequirements(
            num_cores=NUM_CORES,
            distributed=True,
        ),
        execution_level=1,
        num_trials=1,
        input_file_ids=input_file_ids,
        output_file_ids=[id for name, id in file_ids.items() if name != "inp"],
    )

    if use_exec_script:
        exec_script_file = project_api.copy_default_execution_script(
            f"mapdl-v{version[2:4]}{version[6]}-exec_mapdl.py"
        )

        task_def.use_execution_script = True
        task_def.execution_script_id = exec_script_file.id

    task_defs.append(task_def)

    task_def = project_api.create_task_definitions(task_defs)[0]

    return task_def.id, [f for f in files if f.name in ["rst", "mode", "db", "esav", "emat"]]


def create_harmonic_task_definition(
    project_api: ProjectApi, modal_files: List[File], use_exec_script: bool, version: str
) -> str:

    log.info("=== Files")
    cwd = os.path.dirname(__file__)
    # the modal_files output files already exist, no need to create them

    files = [
        File(
            name="inp",
            evaluation_path="harmonic.dat",
            type="text/plain",
            src=os.path.join(cwd, "harmonic.dat"),
        ),
        File(
            name="out", evaluation_path="solve.out", type="text/plain", collect=True, monitor=True
        ),
        File(
            name="err", evaluation_path="file*.err", type="text/plain", collect=True, monitor=True
        ),
    ]

    files = project_api.create_files(files)
    file_ids = {f.name: f.id for f in files}

    # Process step
    input_file_ids = [file_ids["inp"]]
    input_file_ids.extend([f.id for f in modal_files])

    task_defs = []
    task_def = TaskDefinition(
        name="Harmonic",
        software_requirements=[Software(name="Ansys Mechanical APDL", version=version)],
        execution_command="%executable% -b -nolist -i %file:inp% "
        "-o solve.out -np %resource:num_cores%",
        max_execution_time=360.0,
        resource_requirements=ResourceRequirements(
            num_cores=NUM_CORES,
            distributed=True,
        ),
        execution_level=2,
        num_trials=1,
        input_file_ids=input_file_ids,
        output_file_ids=[id for name, id in file_ids.items() if name != "inp"],
    )

    if use_exec_script:
        exec_script_file = project_api.copy_default_execution_script(
            f"mapdl-v{version[2:4]}{version[6]}-exec_mapdl.py"
        )

        task_def.use_execution_script = True
        task_def.execution_script_id = exec_script_file.id

    task_defs.append(task_def)

    task_def = project_api.create_task_definitions(task_defs)[0]

    return task_def.id


def set_last_task_to_pending(project_api: ProjectApi, job_id: str):
    task = project_api.get_tasks(sort="-id", limit=1, job_id=job_id)[0]
    task.eval_status = "pending"
    return project_api.update_tasks([task])


def create_project(
    client: Client, name: str, incremental: bool, use_exec_script: bool, version: str
) -> Project:

    log.info("=== HPS connection")
    log.info(f"Client connected at {client.rep_url}")

    log.info("=== Create new Project")
    if incremental:
        name += " (incremental version)"
    proj = Project(name=name, priority=1, active=True)

    jms_api = JmsApi(client)
    proj = jms_api.create_project(proj)
    log.info(f"Created new project with id={proj.id}")

    project_api = ProjectApi(client, proj.id)

    job_definition = JobDefinition(name="Linked Analyses", active=True)

    log.info("=== Create Prestress task definition")
    prestress_task_def_id, prestress_files = create_prestress_task_definition(
        project_api, use_exec_script, version
    )

    job_definition.task_definition_ids = [prestress_task_def_id]

    if incremental:
        log.info("=== Create Job Definition")
        job_definition = project_api.create_job_definitions([job_definition])[0]
        log.info("=== Submit job")
        job = project_api.create_jobs(
            [Job(eval_status="pending", name="mapdl_job", job_definition_id=job_definition.id)]
        )[0]

    log.info("=== Create Modal task definition")
    modal_task_def_id, modal_files = create_modal_task_definition(
        project_api, prestress_files, use_exec_script, version
    )

    job_definition.task_definition_ids.append(modal_task_def_id)

    if incremental:
        log.info("=== Update Job Definition and Sync job")
        job_definition = project_api.update_job_definitions([job_definition])[0]
        project_api.sync_jobs([job])
        set_last_task_to_pending(project_api, job.id)

    log.info("=== Create Harmonic task definition")
    harmonic_task_def_id = create_harmonic_task_definition(
        project_api, modal_files, use_exec_script, version
    )

    job_definition.task_definition_ids.append(harmonic_task_def_id)

    if incremental:
        log.info("=== Update Job Definition and Sync job")
        job_definition = project_api.update_job_definitions([job_definition])[0]
        project_api.sync_jobs([job])
        set_last_task_to_pending(project_api, job.id)

    else:
        log.info("=== Create Job Definition")
        job_definition = project_api.create_job_definitions([job_definition])[0]
        log.info("=== Submit job")
        job = project_api.create_jobs(
            [Job(eval_status="pending", name="mapdl_job", job_definition_id=job_definition.id)]
        )[0]

    return proj


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, default="MAPDL Prestress-Modal-Harmonic")
    parser.add_argument("-es", "--use-exec-script", default=False, type=bool)
    parser.add_argument("-U", "--url", default="https://localhost:8443/rep")
    parser.add_argument("-u", "--username", default="repadmin")
    parser.add_argument("-p", "--password", default="repadmin")
    parser.add_argument("--incremental", action="store_true")
    parser.add_argument("-v", "--ansys-version", default=__ansys_apps_version__)

    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.INFO)

    log.debug("=== HPS connection")
    client = Client(rep_url=args.url, username=args.username, password=args.password)

    try:
        create_project(
            client,
            name=args.name,
            incremental=args.incremental,
            use_exec_script=args.use_exec_script,
            version=args.ansys_version,
        )
    except REPError as e:
        log.error(str(e))
