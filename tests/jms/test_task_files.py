# ----------------------------------------------------------
# Copyright (C) 2021 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri, O.Koenig
# ----------------------------------------------------------
import datetime
import logging
import os
import time
import unittest

from examples.mapdl_motorbike_frame.project_setup import create_project
from marshmallow.utils import missing

from ansys.rep.client.jms import Client
from ansys.rep.client.jms.resource import File, Task
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class TaskFilesTest(REPTestCase):
    def test_task_files_in_single_task_definition_project(self):
        num_jobs = 5
        client = self.jms_client()
        proj_name = f"test_jobs_TaskFilesTest_{self.run_id}"

        # Setup MAPDL motorbike frame project to work with
        proj = create_project(client=client, name=proj_name, num_jobs=num_jobs)
        proj.active = False
        proj = client.update_project(proj)

        cwd = os.path.dirname(__file__)
        ex_dir = os.path.join(cwd, "..", "..", "examples", "mapdl_motorbike_frame")
        log.info(f"example_dir: {ex_dir}")

        # Create a modified MAPDL input file that reads an extra task file and writes out an extra result file
        mac_file = proj.get_files(limit=1, content=True)[0]
        content = mac_file.content.decode("utf-8")
        lines = content.splitlines()
        for i, l in enumerate(lines):
            if "/PREP7" in l:
                lines.insert(i + 1, "/INPUT,task_input_file,mac")
                break
        for i, l in enumerate(lines):
            if "*CFCLOSE" in l:
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
        tasks = proj.get_tasks()
        for i, t in enumerate(tasks):
            log.info(f"Modify task {t.id}")
            files = []

            # Overwrite modified mac file per task
            files.append(
                File(
                    name="mac",
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
            log.info(f"Add files: {file_ids}")

            t.input_file_ids = [file_ids["mac"], file_ids["mac2"]]
            t.output_file_ids.append(file_ids["task_result"])
            # Not yet supported: t.eval_status = 'pending'

        tasks1 = proj.update_tasks(tasks)
        self.assertEqual(len(tasks1), 5)

        # Check num files existing before evaluation
        for t in tasks1:
            self.assertEqual(len(t.input_file_ids), 2)
            self.assertEqual(len(t.output_file_ids), 1)
            self.assertEqual(len(t.inherited_file_ids), 0)
            self.assertEqual(len(t.owned_file_ids), 3)

        # Wait for the evaluation of all Jobs
        proj.active = True
        client.update_project(proj)

        def wait_for_evaluation_of_all_jobs(proj):
            job_def = proj.get_job_definitions()[0]
            num_jobs_finished = 0
            t1 = datetime.datetime.now()
            dt = 0.0
            task_def = proj.get_task_definitions(job_def.task_definition_ids[0])[0]
            max_eval_time = task_def.max_execution_time * 4
            while num_jobs_finished < num_jobs and dt < max_eval_time:
                jobs = proj.get_jobs(fields=["id", "eval_status"])
                num_jobs_finished = len(
                    [job for job in jobs if job.eval_status in ["evaluated", "timeout", "failed"]]
                )
                log.info(
                    f"Wait for DP evaluations ... num_jobs_finished={num_jobs_finished} dt={dt}"
                )
                time.sleep(5)
                dt = (datetime.datetime.now() - t1).total_seconds()

        wait_for_evaluation_of_all_jobs(proj)

        # Check evaluated design points, tasks and files
        jobs = proj.get_jobs()
        for job in jobs:
            self.assertEqual(job.eval_status, "evaluated")

        def check_evaluated_tasks(proj, tasks):
            for t in tasks:
                log.info(f"=== Task ===")
                log.info(f"id={t.id} eval_status={t.eval_status}")
                log.info(f"input_file_ids={t.input_file_ids} ouptut_file_ids={t.output_file_ids}")
                log.info(
                    f"owned_file_ids={t.owned_file_ids} inherited_file_ids={t.inherited_file_ids}"
                )
                # log.info(f"task_definition_snapshot={t.task_definition_snapshot}")
                self.assertEqual(t.eval_status, "evaluated")
                self.assertEqual(len(t.input_file_ids), 2)
                self.assertEqual(len(t.output_file_ids), 6)
                self.assertEqual(len(t.inherited_file_ids), 5)
                self.assertEqual(len(t.owned_file_ids), 3)

                # All input files are owned by task
                self.assertEqual(len(set(t.input_file_ids).intersection(t.owned_file_ids)), 2)
                input_files = proj.get_files(id=t.input_file_ids)
                self.assertEqual(
                    set([f.name for f in input_files]), set(["mac", "mac2"])
                )  # Check input file names

                owned_output_file_ids = set(t.output_file_ids).intersection(t.owned_file_ids)
                self.assertEqual(len(owned_output_file_ids), 1)  # 1 output file is owned
                owned_output_files = proj.get_files(id=owned_output_file_ids)
                self.assertEqual(owned_output_files[0].name, "task_result")

                inherited_output_file_ids = set(t.output_file_ids).intersection(
                    t.inherited_file_ids
                )
                # 5 output files are inherited
                self.assertEqual(len(inherited_output_file_ids), 5)
                inherited_output_files = proj.get_files(id=inherited_output_file_ids)
                self.assertEqual(
                    set([f.name for f in inherited_output_files]),
                    set(["out", "img", "err", "console_output"]),
                )  # Check output file names

                # Find the task output file and compare the contained variable task_var with task id
                intersection = set(t.output_file_ids).intersection(t.owned_file_ids)
                fid = intersection.pop()
                file = proj.get_files(id=fid, content=True)[0]
                content = file.content.decode("utf-8")
                log.info(f"Task output file id={fid} content={content} task_id={t.id}")
                # Task id must show up in task output file
                self.assertTrue(t.id in content)

        tasks2 = proj.get_tasks()
        check_evaluated_tasks(proj, tasks2)

        # Set project to inactive, reset design points and check what we have
        proj.active = False
        proj = client.update_project(proj)
        jobs = proj.get_jobs(fields=["id", "eval_status"])
        for job in jobs:
            job.eval_status = "pending"
        proj.update_jobs(jobs)
        tasks3 = proj.get_tasks()
        # Compare tasks with the ones created at the begin
        log.info(f"Tasks 1: {[t.id for t in tasks1]}")
        log.info(f"Tasks 3: {[t.id for t in tasks3]}")
        log.info(f"Times1: {[t.creation_time for t in tasks1]}")
        log.info(f"Times3: {[t.creation_time for t in tasks3]}")
        for t1, t3 in zip(tasks1, tasks3):
            self.assertEqual(t1.id, t3.id)
            self.assertEqual(t3.eval_status, "pending")
            self.assertEqual(t1.input_file_ids, t3.input_file_ids)
            self.assertEqual(t1.output_file_ids, t3.output_file_ids)
            self.assertEqual(t1.inherited_file_ids, t3.inherited_file_ids)
            self.assertEqual(t1.owned_file_ids, t3.owned_file_ids)

        # Wait again for the evaluation of all Jobs
        proj.active = True
        proj = client.update_project(proj)
        wait_for_evaluation_of_all_jobs(proj)

        # Check evaluated tasks
        tasks4 = proj.get_tasks()
        check_evaluated_tasks(proj, tasks4)

        # Cleanup
        client.delete_project(proj)

    # TODO
    # def test_task_files_in_multi_task_definition_project(self):


if __name__ == "__main__":
    unittest.main()
