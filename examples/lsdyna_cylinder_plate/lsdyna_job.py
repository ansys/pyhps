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
import json
import logging
import os
import random
import time

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
        repr = json.dumps(self, default=lambda x: x.__dict__, sort_keys=True, indent=4)
        return f"REP Job:\n{repr}"  # noqa: E231

    def save(self):
        """Save job info to JSON file"""
        with open("rep_job.json", "w") as f:
            f.write(json.dumps(self, default=lambda x: x.__dict__, sort_keys=True, indent=4))

    @classmethod
    def load(cls):
        """Load job info from JSON file"""
        with open("rep_job.json", "r") as f:
            job = json.load(f, object_hook=lambda d: cls(**d))
        return job



def submit_job(
    client, name, version=__ansys_apps_version__, num_jobs=20, use_exec_script=False, active=True
) -> REPJob:
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

    app_job = REPJob()
    app_job.project_id = proj.id
    app_job.job_definition_id = job_def.id
    app_job.job_id = [job.id for job in jobs]
    app_job.rep_url = client.rep_url
    app_job.auth_token = client.refresh_token

    return app_job


def monitor_job(app_job: REPJob):
    """
    Monitor the evaluation status of an existing REP job
    """

    # Since we stored the auth token in the job info, there's no need
    # to enter user and password anymore to connect to the REP server.
    client = Client(rep_url=app_job.rep_url, refresh_token=app_job.auth_token)
    project_api = ProjectApi(client, app_job.project_id)

    for job_id in app_job.job_id:
        job = project_api.get_jobs(id=job_id)[0]

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

        for file in files:

            target_folder = os.path.join("job_results", task.task_definition_snapshot.name)
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
                        f"{file.evaluation_path} already exists: "
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

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action", default="submit", choices=["submit", "monitor", "download"], help="Action to run"
    )
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
        if args.action == "submit":            
            job = submit_job(client=client,
                name=args.name,
                version=args.ansys_version,
                num_jobs=args.num_jobs,
                use_exec_script=args.use_exec_script,)
            job.save()           
        elif args.action == "monitor":
            job = REPJob.load()
            log.info(job)
            monitor_job(job)
        elif args.action == "download":
            job = REPJob.load()
            log.info(job)
            download_results(job)
    except HPSError as e:
        log.error(str(e))
