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
Prototype of how to store Fluent Job's data on JMS
"""
import argparse
import logging
import time

from ansys.hps.client import Client, HPSError
from ansys.hps.client.jms import (  # ResourceRequirements,
    JmsApi,
    Job,
    JobDefinition,
    Project,
    ProjectApi,
    Software,
    TaskDefinition,
)

log = logging.getLogger(__name__)


def job_data():
    """This is what Fluent Server would want to store in JMS."""
    data = {"url": "http://localhost:5000", "some_other_data": "value"}
    return data


def run(client: Client, project_name: str):

    jms_api = JmsApi(client)
    proj = Project(name=project_name, priority=1, active=True)
    proj = jms_api.create_project(proj)
    project_api = ProjectApi(client, proj.id)
    log.info(f"Created project '{proj.name}', ID='{proj.id}'")

    task_def = TaskDefinition(
        name="Fluent Session",
        software_requirements=[
            Software(name="Ansys Fluent Server", version="2023 R2"),
        ],
        # for review purposes, could already report this info
        # resource_requirements=ResourceRequirements(
        #     cpu_core_usage=24,
        #     custom={
        #         "unmanaged_fluent_server" : True
        #     }
        # ),
        execution_level=0,
        store_output=False,
    )

    task_def = project_api.create_task_definitions([task_def])[0]

    job_def = JobDefinition(name="JobDefinition", active=True)
    job_def.task_definition_ids = [task_def.id]
    job_def = project_api.create_job_definitions([job_def])[0]

    # here it's important to already mark the job as running
    job = Job(
        name=f"Fluent Session",
        eval_status="running",
        job_definition_id=job_def.id,
    )
    job = project_api.create_jobs([job])[0]
    task = project_api.get_tasks(job_id=job.id)[0]
    task.custom_data = job_data()
    project_api.update_tasks([task])

    log.info(f"You can access your job at {client.url}/jms/#/projects/{proj.id}/jobs/{job.id}")

    time.sleep(60 * 5)
    log.info(f"The job has completed")
    # once the fluent job is complete, you can either
    # 1) remove the corresponding entry in JMS
    # project_api.delete_jobs([job])
    # 2) or mark the JMS job as evaluated/failed
    job.eval_status = "evaluated"
    project_api.update_jobs([job])
    # you could also remove the connection information (since it is no longer valid at this point)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, default="Fluent Job")
    parser.add_argument("-U", "--url", default="https://localhost:8443/rep")
    parser.add_argument("-u", "--username", default="repadmin")
    parser.add_argument("-p", "--password", default="repadmin")
    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="%(message)s", level=logging.INFO)

    try:
        log.info("Connect to REP JMS")
        client = Client(url=args.url, username=args.username, password=args.password)
        run(client=client, project_name=args.name)

    except HPSError as e:
        log.error(str(e))
    except KeyboardInterrupt:
        log.warning("Interrupted, stopping ...")
