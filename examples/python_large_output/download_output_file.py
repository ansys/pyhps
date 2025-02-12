# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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
Example to Download files of evaluated jobs from a project
"""
import argparse
import logging
import os
import tempfile
import time

from ansys.hps.client import Client, HPSError
from ansys.hps.client.jms import JmsApi, ProjectApi

log = logging.getLogger(__name__)


def download_files(client, project_name, dir_path):
    """Download files."""

    out_path = dir_path
    if not out_path:
        temp_dir = tempfile.TemporaryDirectory()
        out_path = os.path.join(temp_dir.name, "downloads")

    log.info(f"Downloading files to {out_path}")

    jms_api = JmsApi(client)
    project = jms_api.get_project_by_name(name=project_name)
    project = jms_api.get_project(id=project.id)

    # start dt client to time download of output files correctly
    jms_api.client._start_dt_worker()

    log.info(f"Project id: {project.id}")
    project_api = ProjectApi(client, project.id)

    jobs = project_api.get_jobs(eval_status="evaluated", fields=["id", "values", "elapsed_time"])
    log.info(f"# evaluated jobs: {len(jobs)}")
    num = len(jobs)

    log.info(f"=== Downloading output files of {num} jobs using ProjectApi.download_file()")
    for job in jobs:
        log.info(f"Job {job.id}")
        for task in project_api.get_tasks(job_id=job.id):
            log.info(f"Task {task.id}")
            files = project_api.get_files(id=task.output_file_ids)
            for f in files:
                fpath = os.path.join(out_path, f"task_{task.id}")
                log.info(f"Download output file {f.evaluation_path} to {fpath}")
                start = time.time()
                project_api.download_file(file=f, target_path=fpath)
                log.info(f"Time taken to download output file: {(time.time() - start):.2f} seconds")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, default="Python Large Output Files")
    parser.add_argument("-U", "--url", default="https://127.0.0.1:8443/hps")
    parser.add_argument("-u", "--username", default="repuser")
    parser.add_argument("-p", "--password", default="repuser")
    parser.add_argument("-dir", "--download-path", type=str)
    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="%(message)s", level=logging.INFO)

    try:
        log.info("Connect to HPC Platform Services")
        client = Client(url=args.url, username=args.username, password=args.password)
        log.info(f"HPS URL: {client.url}")

        download_files(client=client, project_name=args.name, dir_path=args.download_path)

    except HPSError as e:
        log.error(str(e))
