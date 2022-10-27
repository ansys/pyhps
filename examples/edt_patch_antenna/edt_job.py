"""
Script showing how to submit an EDT job to REP.

Once submitted, minimal job information are serialized to a JSON file rep_job.json.
This mimics what an application would need to store in order to
subsequently monitor the job and download results.

Usage:

    $ python edt_job.py submit -n job_name
    $ python edt_job.py monitor
    $ python edt_job.py download
"""

import argparse
import json
import logging
import os
import time

from ansys.rep.client import Client, REPError, __external_version__
from ansys.rep.client.jms import (
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

REP_URL = "https://localhost:8443/rep"
USERNAME = "repadmin"
PASSWORD = "repadmin"
ANSYS_VERSION = "2023 R2"


class REPJob:
    """
    Simplistic helper class to store job information similarly to
    what a pre/post processing application would do.
    """

    def __init__(
        self,
        rep_url=None,
        project_id=None,
        job_definition_id=None,
        job_id=None,
        auth_token=None,
        task_ids=[],
    ):
        self.rep_url = rep_url
        self.project_id = project_id
        self.job_definition_id = job_definition_id
        self.job_id = job_id
        self.auth_token = auth_token
        self.task_ids = task_ids

    def __str__(self):
        return (
            f"REP Job:\n {json.dumps(self, default=lambda x: x.__dict__, sort_keys=True, indent=4)}"
        )

    def save(self):
        """Save job info to JSON file"""
        with open("../../rep_job.json", "w") as f:
            f.write(json.dumps(self, default=lambda x: x.__dict__, sort_keys=True, indent=4))

    @classmethod
    def load(cls):
        """Load job info from JSON file"""
        with open("../../rep_job.json", "r") as f:
            job = json.load(f, object_hook=lambda d: cls(**d))
        return job


def submit_job(name, username, password, rep_url) -> REPJob:
    """Create a REP project running the specified EDT archive job."""

    log.info("=== Connect to the REP server")
    client = Client(rep_url=rep_url, username=username, password=password)
    jms_api = JmsApi(client)

    log.info("=== Create a project")
    proj = Project(name="new " + name, priority=1, active=True)
    proj = jms_api.create_project(proj, replace=True)

    project_api = ProjectApi(client, proj.id)

    log.info("=== Create file resources")
    cwd = os.path.dirname(__file__)
    files = []

    archfile = name + ".aedtz"
    files.append(
        File(
            name="aedtz",
            evaluation_path=archfile,
            type="application/octet-stream",
            src=os.path.join(cwd, archfile),
        )
    )
    files.append(
        File(
            name="result",
            evaluation_path=archfile,
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
    num_input_files = 1
    task_def = TaskDefinition(
        name="AEDT run",
        software_requirements=[
            Software(name="Ansys Electronics Desktop", version="2023 R2"),
        ],
        environment={
            # for extra debugging add
            # "ANSOFT_DEBUG_LOG": "c:\\path\\to\\your\\log\\directory\\prefix-for-log-files",
            # "ANSOFT_DEBUG_MODE": "4",
        },
        use_execution_script=False,  # TODO: In the template version we do use the execution script
        execution_command="%executable% -ng -batchsolve -archiveoptions repackageresults "
        "%file:aedtz%",
        resource_requirements=ResourceRequirements(
            cpu_core_usage=1.0,
            memory=250,
            disk_space=5,
        ),
        execution_level=0,
        execution_context={},
        max_execution_time=50000.0,
        num_trials=1,
        input_file_ids=[f.id for f in files[:num_input_files]],
        output_file_ids=[f.id for f in files[num_input_files:]],
        success_criteria=SuccessCriteria(
            return_code=0,
            required_output_file_ids=[file_ids["result"]],
            require_all_output_files=False,
        ),
        licensing=Licensing(enable_shared_licensing=False),  # Shared licensing disabled by default
    )

    task_defs = project_api.create_task_definitions([task_def])

    job_def.task_definition_ids = [td.id for td in task_defs]

    # Create job_definition in project
    project_api.create_job_definitions([job_def])[0]

    job_def1 = project_api.get_job_definitions()[0]

    log.debug(f"=== Create job")
    job = Job(name=f"Job.0", eval_status="pending", job_definition_id=job_def1.id)
    job1 = project_api.create_jobs([job])[0]

    log.info(f"Created project '{proj.name}', ID='{proj.id}'")

    app_job = REPJob()
    app_job.project_id = proj.id
    app_job.job_definition_id = job_def1.id
    app_job.job_id = job1.id
    app_job.rep_url = client.rep_url
    app_job.auth_token = client.refresh_token

    tasks = project_api.get_tasks(job_id=job1.id)
    job.task_ids = [t.id for t in tasks]

    return app_job


def monitor_job(app_job: REPJob):
    """
    Monitor the evaluation status of an existing REP job
    """

    # Since we stored the auth token in the job info, there's no need
    # to enter user and password anymore to connect to the REP server.
    client = Client(rep_url=app_job.rep_url, refresh_token=app_job.auth_token)
    project_api = ProjectApi(client, app_job.project_id)

    job = project_api.get_jobs(id=app_job.job_id)[0]

    while job.eval_status not in ["evaluated", "timeout", "failed", "aborted"]:
        time.sleep(2)
        log.info(
            f"Waiting for job {job.name} to complete "
            f"[{client.rep_url}/jms/#/projects/{app_job.project_id}/jobs/{job.id}] ... "
        )
        job = project_api.get_jobs(id=job.id)[0]

        tasks = project_api.get_tasks(job_id=job.id)
        for task in tasks:
            log.info(
                f" Task {task.task_definition_snapshot.name} (id={task.id}) is {task.eval_status}"
            )

    log.info(f"Job {job.name} final status: {job.eval_status}")
    return


def download_results(app_job: REPJob):
    """
    Download the job output files (if any)

    Requires the packages tqdm and humanize
    python -m pip install tqdm humanize
    """

    try:
        from tqdm import tqdm
    except ImportError as e:
        log.error("The 'tqdm' package is not installed. Please pip install it")
        return

    try:
        import humanize
    except ImportError as e:
        log.error("The 'humanize' package is not installed. Please pip install it")
        return

    # Since we stored the auth token in the job info, there's no need
    # to enter user and password anymore to connect to the REP server.
    client = Client(rep_url=job.rep_url, refresh_token=app_job.auth_token)
    project_api = ProjectApi(client, app_job.project_id)

    tasks = project_api.get_tasks(job_id=app_job.job_id)

    for task in tasks:

        if not task.output_file_ids:
            log.info(f"No files are available on the server for Task {task.id}")
            continue

        query_params = {"id": task.output_file_ids, "hash.ne": "null"}
        files = project_api.get_files(content=False, **query_params)
        for f in files:
            print(f)
        log.info(
            f"{len(files)} files are available on the server for Task "
            f"{task.id}: {', '.join([f.evaluation_path for f in files])}"
        )

        target_folder = os.path.join("../../job_results", task.task_definition_snapshot.name)
        log.info(f"Files will be downloaded into {target_folder}")
        for file in files:

            download_path = os.path.join(target_folder, file.evaluation_path)

            if os.path.exists(download_path):
                if file.size == os.path.getsize(download_path):
                    log.info(
                        f"Skip download of file "
                        f"{file.evaluation_path} ({humanize.naturalsize(file.size)})"
                    )
                    continue
                else:
                    log.warning(
                        f"{file.evaluation_path} already exists:"
                        f"size on server: {humanize.naturalsize(file.size)}, "
                        f"size on disk {humanize.naturalsize(os.path.getsize(download_path))} MB"
                    )

            log.info(
                f"Start download of file {file.evaluation_path} ({humanize.naturalsize(file.size)})"
            )

            with tqdm(
                total=file.size,
                unit="B",
                unit_scale=True,
                desc=file.evaluation_path,
                initial=0,
                ascii=True,
                ncols=100,
            ) as pbar:
                project_api.download_file(
                    file, target_folder, progress_handler=lambda chunk_size: pbar.update(chunk_size)
                )


if __name__ == "__main__":

    logger = logging.getLogger()
    logging.basicConfig(format="[%(asctime)s | %(levelname)s] %(message)s", level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, default="aedt_tee")
    parser.add_argument("-j", "--num-jobs", type=int, default=1)
    parser.add_argument("-U", "--url", default="https://127.0.0.1:8443/rep")
    parser.add_argument("-u", "--username", default="repadmin")
    parser.add_argument("-p", "--password", default="repadmin")
    parser.add_argument("-v", "--ansys-version", default=__external_version__)
    parser.add_argument(
        "action", default="submit", choices=["submit", "monitor", "download"], help="Action to run"
    )

    args = parser.parse_args()
    try:
        if args.action == "submit":
            job = submit_job(args.name, args.username, args.password, args.url)
            job.save()
        elif args.action == "monitor":
            job = REPJob.load()
            log.info(job)
            monitor_job(job)
        elif args.action == "download":
            job = REPJob.load()
            log.info(job)
            download_results(job)
    except REPError as e:
        log.error(str(e))
    except KeyboardInterrupt:
        log.warning("Interrupted, stopping ...")
