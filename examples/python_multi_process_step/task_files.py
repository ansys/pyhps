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

"""Update some task files
(1) Create a new input file with changed data
(2) change parameter `CALL_SUBSCRIPT` to true in `eval.py`
    that the script is run as subscript with new input file
(3) make sure that newly generated files are added as output of the process step
"""

import json
import logging
import os
from tempfile import NamedTemporaryFile

from ansys.hps.client.jms import File

log = logging.getLogger(__name__)

ADDITIONAL_TASK_FILE = ""


def update_input_file(task):
    log.info(f"Update input file for task {task.task_definition_snapshot.name}")

    data = {
        "color": "white",
        "period": 2,
        "duration": 8,
        "info": f"# changed for task ID: {task.id} task {task.task_definition_snapshot.name}",
    }
    file = NamedTemporaryFile(delete=False, prefix="input_mod", suffix=".json", mode="w")
    json.dump(data, file)
    return file.name


def update_eval_script(task):
    cwd = os.path.dirname(__file__)
    path = os.path.join(cwd, "eval.py")
    lines = open(path).readlines()

    log.info(f"Update input file {path} for task {task.task_definition_snapshot.name}")

    lines = [
        "#" * 20 + "\n",
        "# Changed Task File\n".format(),
        "#" * 20 + "\n",
    ] + lines

    for i, line in enumerate(lines):
        if line.startswith("CALL_SUBSCRIPT = "):
            lines[i] = "CALL_SUBSCRIPT = True\n"

    file = NamedTemporaryFile(
        delete=False,
        mode="w",
        **dict(zip(["prefix", "suffix"], os.path.splitext(os.path.basename(path)), strict=False)),
    )
    file.writelines(lines)
    file.close()
    return file.name


def update_task_files(project_api, num_jobs, write_images):
    log.debug("=== Update Task files ===")

    jobs = project_api.get_jobs(limit=num_jobs)

    # Stop the jobs we're about to change
    for job in jobs:
        job["eval_status"] = "inactive"
    project_api.update_jobs(jobs)
    for job in jobs:
        job["eval_status"] = "pending"

    for dp in jobs:
        log.debug(f" Update job {dp.name}")
        dp.name = dp.name + " Modified"
        tasks = project_api.get_tasks()
        tasks_sel = [t for t in tasks if t.job_id == dp.id]
        for i, task in enumerate(tasks_sel):
            files = []
            # input_file
            ##input_name = "ps_{}_input".format(i)
            ##files.append( File( name=input_name,
            ##                evaluation_path="ps_{}_input.json".format(i),
            ##                type="application/json",
            ##                src=os.path.join(cwd, "input.json".format(i)) ) )
            # new input_file will be used by subprocess
            new_input_file = update_input_file(task)
            new_input_name = f"sub_td{i}_input"
            files.append(
                File(
                    name=new_input_name,
                    evaluation_path=f"sub_td{i}_input.json",
                    type="application/json",
                    src=new_input_file,
                )
            )
            # overwrite the eval script: same name --> will be overwritten
            new_eval_script = update_eval_script(task)
            new_eval_name = f"td{i}_pyscript"
            files.append(
                File(
                    name=new_eval_name,
                    evaluation_path="eval.py",
                    type="text/plain",
                    src=new_eval_script,
                )
            )
            # output text
            # out_name = "ps_{}_results".format(i)
            # files.append( File( name=out_name,
            #                evaluation_path="ps_{}_results.txt".format(i),
            #                collect=True, monitor=True,
            #                type="text/plain" ) )
            # new output text
            new_out_name = f"sub_td{i}_results"
            files.append(
                File(
                    name=new_out_name,
                    evaluation_path=f"sub_td{i}_results.txt",
                    collect=True,
                    monitor=True,
                    type="text/plain",
                )
            )
            # new image
            if write_images:
                new_image_name = f"sub_td{i}_results_jpg"
                files.append(
                    File(
                        name=new_image_name,
                        evaluation_path=f"sub_td{i}_results.jpg",
                        type="image/jpeg",
                        collect=True,
                    )
                )

            files = project_api.create_files(files)
            file_ids = {f.name: f.id for f in files}

            output_file_ids = [file_ids[new_out_name]]
            if write_images:
                output_file_ids.append(file_ids[new_image_name])

            task.output_file_ids = output_file_ids
            task.input_file_ids = [file_ids[new_input_name], file_ids[new_eval_name]]

        project_api.update_tasks(tasks_sel)

    project_api.update_jobs(jobs)
    log.info(f"Updated {len(jobs)} design points")
