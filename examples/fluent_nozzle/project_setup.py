"""
Example script to setup a simple Fluent project in pyrep.
"""
import argparse
import logging
import os

from ansys.hps.client import Client, HPSError, __ansys_apps_version__
from ansys.hps.client.jms import (
    File,
    JmsApi,
    Job,
    JobDefinition,
    Licensing,
    Project,
    ProjectApi,
    ResourceRequirements,
    Software,
    SuccessCriteria,
    TaskDefinition,
)

log = logging.getLogger(__name__)


def create_project(client, name, num_jobs=20, version=__ansys_apps_version__):
    """
    Create a REP project consisting of an Ansys Fluent model.
    """
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
            name="inp",
            evaluation_path="nozzle.cas",
            type="text/plain",
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
            name="exec_fluent",
            evaluation_path="exec_fluent.py",
            type="application/x-python-code",
            src=os.path.join(cwd, "exec_fluent.py"),
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

    # Task definition
    num_input_files = 3
    task_def = TaskDefinition(
        name="Fluent_run",
        software_requirements=[
            Software(name="Ansys Fluent", version=version),
        ],
        execution_command=None,  # Only execution currently supported
        resource_requirements=ResourceRequirements(
            num_cores=1.0,
            memory=250,
            disk_space=5,
        ),
        execution_level=0,
        execution_context={
            "fluent_dimension": "3d",
            "fluent_precision": "dp",
            "fluent_meshing": False,
            "fluent_numGPGPUsPerMachine": 0,
            "fluent_MPIType": "intel",
            "fluent_otherEnvironment": "{}",
            "fluent_useGUI": False,
        },
        max_execution_time=50.0,
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
        licensing=Licensing(enable_shared_licensing=False),  # Shared licensing disabled by default
    )

    task_def.use_execution_script = True
    task_def.execution_command = None
    task_def.execution_script_id = file_ids["exec_fluent"]

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
    parser.add_argument("-n", "--name", type=str, default="fluent_nozzle")
    parser.add_argument("-j", "--num-jobs", type=int, default=1)
    parser.add_argument("-es", "--use-exec-script", default=True, action="store_true")
    parser.add_argument("-U", "--url", default="https://127.0.0.1:8443/hps")
    parser.add_argument("-u", "--username", default="repadmin")
    parser.add_argument("-p", "--password", default="repadmin")
    parser.add_argument("-v", "--ansys-version", default=__ansys_apps_version__)
    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    try:
        log.info("Connect to HPC Platform Services")
        client = Client(rep_url=args.url, username=args.username, password=args.password)
        log.info(f"HPS URL: {client.rep_url}")
        proj = create_project(
            client=client, name=args.name, num_jobs=args.num_jobs, version=args.ansys_version
        )

    except HPSError as e:
        log.error(str(e))
