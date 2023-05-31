"""
This example shows how to submit a simple Fluent 2D job to REP.
"""

import argparse
import logging
import os

from ansys.rep.client import Client, REPError, __ansys_apps_version__
from ansys.rep.client.jms import (
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

log = logging.getLogger(__name__)


def main(client: Client, name: str, version: str) -> Project:

    log.info("=== Create Project")
    jms_api = JmsApi(client)
    proj = Project(name=name, priority=1, active=True)
    proj = jms_api.create_project(proj)

    project_api = ProjectApi(client, proj.id)

    log.info("=== Create Files")
    cwd = os.path.dirname(__file__)

    files = [
        File(
            name="cas_h5",
            evaluation_path="heat_exchanger.cas.h5",
            type="application/octet-stream",
            src=os.path.join(cwd, "heat_exchanger.cas.h5"),
        ),
        File(
            name="journal",
            evaluation_path="heat_exchanger.jou",
            type="text/plain",
            src=os.path.join(cwd, "heat_exchanger.jou"),
        ),
        File(
            name="trn", evaluation_path="fluent*.trn", type="text/plain", collect=True, monitor=True
        ),
        File(
            name="output_cas",
            evaluation_path="output_results.cas.h5",
            type="application/octet-stream",
            collect=True,
            monitor=False,
        ),
        File(
            name="output_data",
            evaluation_path="output_results.data.dat.h5",
            type="application/octet-stream",
            collect=True,
            monitor=False,
        ),
    ]

    files = project_api.create_files(files)
    file_ids = {f.name: f.id for f in files}

    log.debug("=== Job Definition with simulation workflow")

    # Task Definition
    task_def = TaskDefinition(
        name="Fluent Run",
        software_requirements=[Software(name="Ansys Fluent", version=version)],
        execution_command="%executable% 2d -g -tm %resource:num_cores% -i %file:journal%",
        resource_requirements=ResourceRequirements(
            cpu_core_usage=4,
            memory=4000,
            disk_space=500,
        ),
        max_execution_time=600.0,
        execution_level=0,
        num_trials=1,
        input_file_ids=[file_ids["cas_h5"], file_ids["journal"]],
        output_file_ids=[file_ids["trn"], file_ids["output_cas"], file_ids["output_data"]],
    )
    task_def = project_api.create_task_definitions([task_def])[0]

    # Create job_definition in project
    job_def = JobDefinition(name="JobDefinition.1", active=True)
    job_def.task_definition_ids = [task_def.id]
    job_def = project_api.create_job_definitions([job_def])[0]

    log.info("=== Submit Job")
    job = project_api.create_jobs(
        [Job(name=f"Job", eval_status="pending", job_definition_id=job_def.id)]
    )[0]

    log.info(f"Created project '{proj.name}', ID='{proj.id}'")
    log.info(
        f"You can monitor the job status at "
        f"{project_api.client.rep_url}/jms/#/projects/{project_api.project_id}/jobs/{job.id}"
    )

    return proj


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, default="Fluent 2D Heat Exchanger")
    parser.add_argument("-U", "--url", default="https://localhost:8443/rep")
    parser.add_argument("-u", "--username", default="repadmin")
    parser.add_argument("-p", "--password", default="repadmin")
    parser.add_argument("-v", "--ansys-version", default=__ansys_apps_version__)

    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.DEBUG)

    log.debug("=== REP connection")
    client = Client(rep_url=args.url, username=args.username, password=args.password)

    try:
        main(client, name=args.name, version=args.ansys_version)
    except REPError as e:
        log.error(str(e))
