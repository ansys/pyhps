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

import datetime
import logging
import os
import time

import pytest
from ansys.hps.client.jms import JmsApi, ProjectApi
from ansys.hps.client.jms.resource import File

from examples.mapdl_motorbike_frame.project_setup import create_project

log = logging.getLogger(__name__)


@pytest.mark.skip(reason="Requires an evaluator with MAPDL.")
def test_task_files_in_single_task_definition_project(client):
    num_jobs = 5
    proj_name = "test_jobs_TaskFilesTest"

    # Setup MAPDL motorbike frame project to work with
    proj = create_project(client=client, name=proj_name, num_jobs=num_jobs)
    proj.active = False
    jms_api = JmsApi(client)
    proj = jms_api.update_project(proj)

    project_api = ProjectApi(client, proj.id)

    cwd = os.path.dirname(__file__)
    ex_dir = os.path.join(cwd, "..", "..", "examples", "mapdl_motorbike_frame")
    log.info(f"example_dir: {ex_dir}")

    # Create a modified MAPDL input file that reads an extra task file
    # and writes out an extra result file
    mac_file = project_api.get_files(limit=1, content=True)[0]
    content = mac_file.content.decode("utf-8")
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if "/PREP7" in line:
            lines.insert(i + 1, "/INPUT,task_input_file,mac")
            break
    for i, line in enumerate(lines):
        if "*CFCLOSE" in line:
            lines.insert(i + 2, "*CFCLOSE")
            # lines.insert(i+2, "('task_var = ',F20.8)")
            lines.insert(i + 2, "'task_var = %C'")
            lines.insert(i + 2, "*VWRITE,task_var")
            lines.insert(i + 2, "*CFOPEN,task_output_file,txt")
            break
    mac_fpath = os.path.join(ex_dir, "motorbike_frame_mod.mac")
    with open(mac_fpath, "w") as f:
        f.write("\n".join(lines))

    # Add specific task files to tasks
    tasks = project_api.get_tasks()
    for i, t in enumerate(tasks):
        log.info(f"Modify task {t.id}")
        files = []

        # Overwrite modified mac file per task
        files.append(
            File(
                name="inp",
                evaluation_path="motorbike_frame.mac",
                type="text/plain",
                src=mac_fpath,
            )
        )

        # Add an extra task input file containing a variable with task id
        mac2_fpath = os.path.join(ex_dir, f"task_input_file_{i}.mac")
        with open(mac2_fpath, "w") as f:
            f.write(f"task_var='{t.id}'")
        files.append(
            File(
                name="inp2",
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

        files = project_api.create_files(files)
        file_ids = {f.name: f.id for f in files}
        log.info(f"Add files: {file_ids}")

        t.input_file_ids = [file_ids["inp"], file_ids["inp2"]]
        t.output_file_ids.append(file_ids["task_result"])
        # Not yet supported: t.eval_status = 'pending'

    tasks1 = project_api.update_tasks(tasks)
    assert len(tasks1) == 5

    # Check num files existing before evaluation
    for t in tasks1:
        assert len(t.input_file_ids) == 2
        assert len(t.output_file_ids) == 1
        assert len(t.inherited_file_ids) == 0
        assert len(t.owned_file_ids) == 3

    # Wait for the evaluation of all Jobs
    proj.active = True
    jms_api.update_project(proj)

    def wait_for_evaluation_of_all_jobs(project_api):
        job_def = project_api.get_job_definitions()[0]
        num_jobs_finished = 0
        t1 = datetime.datetime.now()
        dt = 0.0
        task_def = project_api.get_task_definitions(job_def.task_definition_ids[0])[0]
        max_eval_time = task_def.max_execution_time * 4
        while num_jobs_finished < num_jobs and dt < max_eval_time:
            jobs = project_api.get_jobs(fields=["id", "eval_status"])
            num_jobs_finished = len(
                [job for job in jobs if job.eval_status in ["evaluated", "timeout", "failed"]]
            )
            log.info(f"Wait for DP evaluations ... num_jobs_finished={num_jobs_finished} dt={dt}")
            time.sleep(5)
            dt = (datetime.datetime.now() - t1).total_seconds()

    wait_for_evaluation_of_all_jobs(project_api)

    # Check evaluated design points, tasks and files
    jobs = project_api.get_jobs()
    for job in jobs:
        assert job.eval_status == "evaluated"

    def check_evaluated_tasks(project_api, tasks):
        for t in tasks:
            log.info("=== Task ===")
            log.info(f"id={t.id} eval_status={t.eval_status}")
            log.info(f"input_file_ids={t.input_file_ids} ouptut_file_ids={t.output_file_ids}")
            log.info(f"owned_file_ids={t.owned_file_ids} inherited_file_ids={t.inherited_file_ids}")
            # log.info(f"task_definition_snapshot={t.task_definition_snapshot}")
            assert t.eval_status == "evaluated"
            assert len(t.input_file_ids) == 2
            assert len(t.output_file_ids) == 6
            assert len(t.inherited_file_ids) == 5
            assert len(t.owned_file_ids) == 3

            # All input files are owned by task
            assert len(set(t.input_file_ids).intersection(t.owned_file_ids)) == 2
            input_files = project_api.get_files(id=t.input_file_ids)
            # Check input file names
            assert {f.name for f in input_files} == {"inp", "inp2"}

            owned_output_file_ids = set(t.output_file_ids).intersection(t.owned_file_ids)
            assert len(owned_output_file_ids) == 1  # 1 output file is owned
            owned_output_files = project_api.get_files(id=owned_output_file_ids)
            assert owned_output_files[0].name == "task_result"

            inherited_output_file_ids = set(t.output_file_ids).intersection(t.inherited_file_ids)
            # 5 output files are inherited
            assert len(inherited_output_file_ids) == 5
            inherited_output_files = project_api.get_files(id=inherited_output_file_ids)
            # Check output file names
            assert {f.name for f in inherited_output_files} == {
                "out",
                "img",
                "err",
                "console_output",
            }

            # Find the task output file and compare the contained variable task_var with task id
            intersection = set(t.output_file_ids).intersection(t.owned_file_ids)
            fid = intersection.pop()
            file = project_api.get_files(id=fid, content=True)[0]
            content = file.content.decode("utf-8")
            log.info(f"Task output file id={fid} content={content} task_id={t.id}")
            # Task id must show up in task output file
            assert t.id in content

    tasks2 = project_api.get_tasks()
    check_evaluated_tasks(project_api, tasks2)

    # Set project to inactive, reset design points and check what we have
    proj.active = False
    proj = jms_api.update_project(proj)
    jobs = project_api.get_jobs(fields=["id", "eval_status"])
    for job in jobs:
        job.eval_status = "pending"
    project_api.update_jobs(jobs)
    tasks3 = project_api.get_tasks()
    # Compare tasks with the ones created at the begin
    log.info(f"Tasks 1: {[t.id for t in tasks1]}")
    log.info(f"Tasks 3: {[t.id for t in tasks3]}")
    log.info(f"Times1: {[t.creation_time for t in tasks1]}")
    log.info(f"Times3: {[t.creation_time for t in tasks3]}")
    for t1, t3 in zip(tasks1, tasks3, strict=False):
        assert t1.id == t3.id
        assert t3.eval_status == "pending"
        # use assertCountEqual to verify that the lists have
        # the same elements, the same number of times, without regard to order.
        assert sorted(t1.input_file_ids) == sorted(t3.input_file_ids)
        assert sorted(t1.output_file_ids) == sorted(t3.output_file_ids)
        assert sorted(t1.inherited_file_ids) == sorted(t3.inherited_file_ids)
        assert sorted(t1.owned_file_ids) == sorted(t3.owned_file_ids)

    # Wait again for the evaluation of all Jobs
    proj.active = True
    proj = jms_api.update_project(proj)
    wait_for_evaluation_of_all_jobs(project_api)

    # Check evaluated tasks
    tasks4 = project_api.get_tasks()
    check_evaluated_tasks(project_api, tasks4)

    # Cleanup
    jms_api.delete_project(proj)
