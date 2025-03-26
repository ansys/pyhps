# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
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

"""Example to modify task files in a simple rep task definition."""

import argparse
import logging
import os

from ansys.hps.client import HPSError
from ansys.hps.client.jms import Client, File

log = logging.getLogger(__name__)


def modify_task_files(client, project_name):
    """Modify task files mapdl_motorbike_frame project."""
    cwd = os.path.dirname(__file__)

    proj = client.get_project(name=project_name)
    # Todo: Fix needed in the backend:
    # Currently only the get_project() called with id returns all fields of project.
    proj = client.get_project(id=proj.id)

    log.info(f"proj={proj}")

    # Identify mac input file in task definition
    # We have only 1 task definition
    task_def = proj.get_task_definitions()[0]
    # We have only 1 input file
    mac_file_id = task_def.input_file_ids[0]
    log.info(f"mac_file_id={mac_file_id}")

    # Todo: Fixme: The rest of the example does not yet work,
    # the proj object seems to miss file storage information

    # Create a modified MAPDL input file that reads an extra task file
    # and writes out an extra result file
    mac_file = proj.get_files(id=mac_file_id, content=True)[0]
    content = mac_file.content.decode("utf-8")
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if "/PREP7" in line:
            lines.insert(i + 1, "/INPUT,task_input_file,mac")
            break
    for i, line in enumerate(lines):
        if "*CFCLOSE" in line:
            lines.insert(i + 2, "*CFCLOSE")
            lines.insert(i + 2, "('task_var = ',F20.8)")
            lines.insert(i + 2, "*VWRITE,task_var")
            lines.insert(i + 2, "*CFOPEN,task_output_file,txt")
            break
    mac_fpath = os.path.join(cwd, "motorbike_frame_mod.mac")
    with open(mac_fpath, "w") as f:
        f.write("\n".join(lines))

    # Add specific task files to tasks
    tasks = proj.get_tasks(limit=5)
    for i, t in enumerate(tasks):
        log.debug(f"Modify task {t.id}")
        files = []

        # Overwrite modified mac file per task
        files.append(
            File(
                name="mac", evaluation_path="motorbike_frame.mac", type="text/plain", src=mac_fpath
            )
        )

        # Add an extra task input file
        mac2_fpath = os.path.join(cwd, f"task_input_file_{t.id}.mac")
        with open(mac2_fpath, "w") as f:
            f.write(f"task_var={i}")
        files.append(
            File(
                name="mac2",
                evaluation_path="task_input_file.mac",
                type="text/plain",
                src=mac2_fpath,
            )
        )

        # Add an extra task output file
        files.append(
            File(
                name="task_result",
                evaluation_path="task_output_file.txt",
                type="text/plain",
                collect=True,
            )
        )

        files = proj.create_files(files)
        file_ids = {f.name: f.id for f in files}
        log.debug(f"Add files: {file_ids}")

        t.input_file_ids = [file_ids["mac"], file_ids["mac2"]]
        t.output_file_ids.append(file_ids["task_result"])
        # Not yet supported: t.eval_status = 'pending'

    tasks = proj.update_tasks(tasks)

    # Set affected design points back to pending
    # (directly setting tasks back to pending is not yet supported)
    dp_ids = [t.job_id for t in tasks]
    jobs = proj.get_jobs(id=dp_ids)
    for job in jobs:
        job.eval_status = "pending"
    proj.update_jobs(jobs)

    log.debug("=== Modified tasks and design points:")
    for t, _ in zip(tasks, jobs, strict=False):
        msg = f"Task: id={t.id} eval_status={t.eval_status} "
        msg += "input_file_ids={t.input_file_ids} ouptut_file_ids={t.output_file_ids} "
        msg += "Job: id={dp.id} eval_status={dp.eval_status}"
        log.debug(msg)

        # log.debug(f'{t}')
        # log.debug(f'{dp}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", type=str, default="mapdl_motorbike_frame")
    parser.add_argument("-j", "--num-jobs", type=int, default=500)
    parser.add_argument("-U", "--url", default="https://127.0.0.1:8443/hps")
    parser.add_argument("-u", "--username", default="repuser")
    parser.add_argument("-p", "--password", default="repuser")
    args = parser.parse_args()

    logger = logging.getLogger()
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)

    try:
        log.info("Connect to HPC Platform Services")
        client = Client(url=args.url, username=args.username, password=args.password)
        log.info(f"HPS URL: {client.url}")

        modify_task_files(client=client, project_name=args.name)
    except HPSError as e:
        log.error(str(e))
