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
Example to query resources from a project.

- Query values from evaluated jobs, computing some simple statistics on parameter values.
- Download files from the project

"""
import argparse
import logging
import os
from statistics import mean, stdev

from ansys.hps.client import Client, HPSError
from ansys.hps.client.jms import JmsApi, ProjectApi

log = logging.getLogger(__name__)


def print_value_stats(values, title):
    """Print value stats."""
    log.info(f"{title}")
    # log.info(f"Num      : {len(values)}")
    log.info(f"Mean     : {mean(values)} Stdev: {stdev(values)}")
    log.info(f"(Min, Max): ({min(values)}, {max(values)})")


def query_stats(client, project_name):
    """Query statistics."""
    log.info("=== Query values and compoute statistics ===")
    jms_api = JmsApi(client)
    log.info("=== Project")
    project = jms_api.get_project_by_name(name=project_name)
    log.info(f"ID: {project.id}")
    log.info(f"Created on: {project.creation_time}")

    project_api = ProjectApi(client, project.id)

    log.info("=== Query jobs")
    jobs = project_api.get_jobs(eval_status="evaluated", fields=["id", "values", "elapsed_time"])
    if not jobs:
        log.info("No evaluated jobs found to compute statistics from, exiting")
        return

    log.info(f"Statistics across {len(jobs)} jobs")

    values = [job.values["mapdl_elapsed_time_obtain_license"] for job in jobs]
    print_value_stats(
        values, "=== License checkoput (parameter: mapdl_elapsed_time_obtain_license)"
    )

    values = [job.values["mapdl_elapsed_time"] for job in jobs]
    print_value_stats(values, "=== Elapsed time MAPDL (mapdl_elapsed_time)")

    values = [job.elapsed_time for job in jobs]
    print_value_stats(values, "=== Elapsed time REP (elapsed_time)")

    log.info("=== Query tasks")
    tasks = project_api.get_tasks(
        eval_status="evaluated", fields=["id", "prolog_time", "running_time", "finished_time"]
    )
    log.info("Statistics across tasks")

    values = [(t.running_time - t.prolog_time).total_seconds() for t in tasks]
    print_value_stats(values, "=== Prolog time (running_time - prolog_time")

    values = [(t.finished_time - t.running_time).total_seconds() for t in tasks]
    print_value_stats(values, "=== Running time (finished_time - running_time")


def download_files(client, project_name):
    """Download files."""
    out_path = os.path.join(os.path.dirname(__file__), "downloads")
    log.info(f"Downloading files to {out_path}")

    jms_api = JmsApi(client)
    project = jms_api.get_project_by_name(name=project_name)
    # Todo: Fix needed in the backend:
    # Currently only the get_project() called with id returns all fields of project.
    project = jms_api.get_project(id=project.id)

    log.info(f"Project id: {project.id}")
    project_api = ProjectApi(client, project.id)

    jobs = project_api.get_jobs(eval_status="evaluated", fields=["id", "values", "elapsed_time"])
    log.info(f"# evaluated jobs: {len(jobs)}")
    num = min(len(jobs), 10)

    log.info(
        f"=== Example 1: Downloading output files of {num} jobs using ProjectApi.download_file()"
    )
    for job in jobs[0:num]:
        log.info(f"Job {job.id}")
        for task in project_api.get_tasks(job_id=job.id):
            log.info(f"Task {task.id}")
            files = project_api.get_files(id=task.output_file_ids)
            for f in files:
                fpath = os.path.join(out_path, f"task_{task.id}")
                log.info(f"Download output file {f.evaluation_path} to {fpath}")
                project_api.download_file(file=f, target_path=fpath)

    num = 10
    files = project_api.get_files(type="image/jpeg", limit=num, content=True)
    num = len(jobs)
    log.info(f"=== Example 2: Global download of {num} jpeg images in project using content=True")
    for f in files:
        if f.content:
            fpath = os.path.join(out_path, f"task_{f.id}_{f.evaluation_path}")
            log.info(f"Download image file to {fpath}")
            with open(fpath, "wb") as bf:
                bf.write(f.content)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, default="Mapdl Motorbike Frame")
    parser.add_argument("-j", "--num-jobs", type=int, default=500)
    parser.add_argument("-U", "--url", default="https://127.0.0.1:8443/rep")
    parser.add_argument("-u", "--username", default="repadmin")
    parser.add_argument("-p", "--password", default="repadmin")
    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    try:
        log.info("Connect to HPC Platform Services")
        client = Client(rep_url=args.url, username=args.username, password=args.password)
        log.info(f"HPS URL: {client.rep_url}")

        query_stats(client=client, project_name=args.name)
        download_files(client=client, project_name=args.name)

    except HPSError as e:
        log.error(str(e))
