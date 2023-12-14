# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------
import datetime
import logging
import time
import unittest
import uuid

from examples.mapdl_motorbike_frame.project_setup import create_project
from marshmallow.utils import missing
import pytest

from ansys.hps.client.jms import JmsApi, ProjectApi
from ansys.hps.client.jms.resource import Job, JobDefinition, Project, Software, TaskDefinition
from ansys.hps.client.jms.schema.task import TaskSchema
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class TasksTest(REPTestCase):
    def test_task_deserialization(self):

        task_dict = {
            "id": "02q3zCLSbavqZAeO3VjChL",
            "modification_time": "2021-02-26T09:02:47.818186+00:00",
            "creation_time": "2021-02-26T09:02:11.999810+00:00",
            "pending_time": "2021-02-26T09:02:12.464568+00:00",
            "prolog_time": "2021-02-26T09:02:26.669714+00:00",
            "running_time": "2021-02-26T09:02:27.087597+00:00",
            "finished_time": "2021-02-26T09:02:47.821178+00:00",
            "eval_status": "evaluated",
            "trial_number": 1,
            "elapsed_time": 20.733581,
            "task_definition_id": "02q3zCLSZjRkJhCzjVjyYn",
            "job_id": "02q3zCLScqou7nbJBXFEfw",
            "host_id": "9be2d91a-abb1-3b68-bc36-d23a990a9792",
            "license_context_id": None,
            "input_file_ids": ["02q3zEBtQFm0UcdNSLPvC9"],
            "output_file_ids": [
                "02q3zEBtYSW3PYPwMOc6qu",
                "02q3zEBtV1yvNkLDw7PSWd",
                "02q3zEBtXIlsgj8Td92lzI",
                "02q3zEBtZ0oVfoCAEBDiP5",
                "02q3zEBtXfh5XvEnWc9c0w",
            ],
            "inherited_file_ids": ["02q3zEBtQFm0UcdNSLPvC9"],
            "owned_file_ids": [
                "02q3zEBtYSW3PYPwMOc6qu",
                "02q3zEBtV1yvNkLDw7PSWd",
                "02q3zEBtXIlsgj8Td92lzI",
                "02q3zEBtZ0oVfoCAEBDiP5",
                "02q3zEBtXfh5XvEnWc9c0w",
            ],
            "custom_data": {"key": "value"},
        }

        task = TaskSchema().load(task_dict)

        self.assertEqual(task.id, "02q3zCLSbavqZAeO3VjChL")
        self.assertEqual(task.__class__.__name__, "Task")
        self.assertEqual(task.eval_status, "evaluated")
        self.assertEqual(task.trial_number, 1)
        self.assertAlmostEqual(task.elapsed_time, 20.733581)
        self.assertEqual(task.task_definition_id, "02q3zCLSZjRkJhCzjVjyYn")
        self.assertEqual(task.job_id, "02q3zCLScqou7nbJBXFEfw")
        self.assertEqual(task.host_id, "9be2d91a-abb1-3b68-bc36-d23a990a9792")
        # self.assertEqual( task.uuid, "f6775a29-d98b-4048-a14d-ea86669e55d0")
        # self.assertEqual( task.license_context_id, None)
        self.assertEqual(task.input_file_ids, ["02q3zEBtQFm0UcdNSLPvC9"])
        self.assertEqual(
            task.output_file_ids,
            [
                "02q3zEBtYSW3PYPwMOc6qu",
                "02q3zEBtV1yvNkLDw7PSWd",
                "02q3zEBtXIlsgj8Td92lzI",
                "02q3zEBtZ0oVfoCAEBDiP5",
                "02q3zEBtXfh5XvEnWc9c0w",
            ],
        )
        self.assertEqual(task.inherited_file_ids, ["02q3zEBtQFm0UcdNSLPvC9"])
        self.assertEqual(
            task.owned_file_ids,
            [
                "02q3zEBtYSW3PYPwMOc6qu",
                "02q3zEBtV1yvNkLDw7PSWd",
                "02q3zEBtXIlsgj8Td92lzI",
                "02q3zEBtZ0oVfoCAEBDiP5",
                "02q3zEBtXfh5XvEnWc9c0w",
            ],
        )
        self.assertEqual(task.custom_data, {"key": "value"})

    def test_task_integration(self):

        client = self.client
        proj_name = "Mapdl Motorbike Frame"

        project = create_project(client, proj_name, num_jobs=5, use_exec_script=False)

        project_api = ProjectApi(client, project.id)
        tasks = project_api.get_tasks(limit=5)
        self.assertEqual(len(tasks), 5)

        jobs = project_api.get_jobs(limit=5)
        for job in jobs:
            tasks = project_api.get_tasks(job_id=job.id)
            self.assertEqual(tasks[0].job_id, job.id)
            self.assertTrue(tasks[0].created_by is not missing)
            self.assertTrue(tasks[0].modified_by is not missing)

    def test_job_sync(self):

        # create base project with 1 task and 3 jobs
        num_jobs = 3
        client = self.client
        jms_api = JmsApi(client)
        proj_name = f"test_desing_point_sync_{uuid.uuid4().hex[:8]}"

        project = Project(name=proj_name, active=False, priority=10)
        project = jms_api.create_project(project, replace=True)
        project_api = ProjectApi(client, project.id)

        task_def_1 = TaskDefinition(
            name="Task.1",
            software_requirements=[Software(name="NonExistingApp", version="1.0.0")],
            execution_command="%executable%",
            max_execution_time=10.0,
            execution_level=0,
            num_trials=1,
        )
        task_def_1 = project_api.create_task_definitions([task_def_1])[0]
        job_def = JobDefinition(
            name="JobDefinition.1", active=True, task_definition_ids=[task_def_1.id]
        )
        job_def = project_api.create_job_definitions([job_def])[0]

        jobs = []
        for i in range(num_jobs):
            jobs.append(Job(name=f"Job.{i}", eval_status="pending", job_definition_id=job_def.id))
        jobs = project_api.create_jobs(jobs)

        for job in jobs:
            tasks = project_api.get_tasks(job_id=job.id)
            self.assertEqual(len(tasks), 1)
            self.assertEqual(tasks[0].eval_status, "pending")

        # add a second task
        task_def_2 = TaskDefinition(
            name="Task.2",
            software_requirements=[Software(name="NonExistingApp", version="1.0.0")],
            execution_command="%executable%",
            max_execution_time=10.0,
            execution_level=1,
            num_trials=1,
        )
        task_def_2 = project_api.create_task_definitions([task_def_2])[0]
        job_def = project_api.get_job_definitions()[0]
        job_def.task_definition_ids.append(task_def_2.id)
        job_def = project_api.update_job_definitions([job_def])[0]

        # sync jobs individually
        jobs = project_api.get_jobs()
        project_api.sync_jobs(jobs)

        # verify that tasks were added and they're inactive
        for job in jobs:
            tasks = project_api.get_tasks(job_id=job.id)
            self.assertEqual(len(tasks), 2)
            self.assertEqual(tasks[0].eval_status, "pending")
            self.assertEqual(tasks[0].task_definition_snapshot.name, "Task.1")
            self.assertEqual(tasks[1].eval_status, "inactive")

        # set new tasks to pending
        tasks = project_api.get_tasks(eval_status="inactive")
        for task in tasks:
            task.eval_status = "pending"
        project_api.update_tasks(tasks)

        # verify that tasks are pending and that task_definition_snapshots were created
        for job in jobs:
            tasks = project_api.get_tasks(job_id=job.id)
            self.assertEqual(len(tasks), 2)
            self.assertEqual(tasks[0].eval_status, "pending")
            self.assertEqual(tasks[0].task_definition_snapshot.name, "Task.1")
            self.assertEqual(tasks[1].eval_status, "pending")
            self.assertEqual(tasks[1].task_definition_snapshot.name, "Task.2")

        # add a third process step
        task_def_3 = TaskDefinition(
            name="Task.3",
            software_requirements=[Software(name="NonExistingApp", version="1.0.0")],
            execution_command="%executable%",
            max_execution_time=10.0,
            execution_level=0,
            num_trials=1,
        )
        task_def_3 = project_api.create_task_definitions([task_def_3])[0]
        job_def.task_definition_ids.append(task_def_3.id)
        job_def = project_api.update_job_definitions([job_def])[0]

        # sync the first 2 design points in bulk
        project_api.sync_jobs(jobs[:2])

        # verify that tasks were added and they're inactive
        for job in jobs[:2]:
            tasks = project_api.get_tasks(job_id=job.id)
            self.assertEqual(len(tasks), 3)
            self.assertEqual(tasks[0].eval_status, "pending")
            self.assertEqual(tasks[1].eval_status, "pending")
            self.assertEqual(tasks[2].eval_status, "inactive")

        # verify that the third task wasn't added for DP2
        tasks = project_api.get_tasks(job_id=jobs[2].id)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].eval_status, "pending")
        self.assertEqual(tasks[1].eval_status, "pending")

        jms_api.delete_project(project)

    def wait_for_evaluation_of_job(self, project_api, job_id, max_eval_time):
        job = project_api.get_jobs(id=job_id)[0]
        t1 = datetime.datetime.now()
        dt = 0.0
        while (
            job.eval_status not in ["evaluated", "timeout", "failed", "aborted"]
            and dt < max_eval_time
        ):
            time.sleep(2)
            log.info(f"   Waiting for job '{job.name}' to complete ... ")
            job = project_api.get_jobs(id=job_id)[0]
            dt = (datetime.datetime.now() - t1).total_seconds()

        return job

    @pytest.mark.requires_evaluator
    def test_sync_task_definition_snapshot(self):
        # verity that the process step snapshot of an evaluated task in not modified
        # on job:sync

        client = self.client
        proj_name = f"test_sync_task_definition_snapshot_{uuid.uuid4().hex[:8]}"

        project = create_project(client=client, name=proj_name, num_jobs=1)
        project_api = ProjectApi(client, project.id)

        job = project_api.get_jobs()[0]
        tasks = project_api.get_tasks(job_id=job.id)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(
            tasks[0].task_definition_snapshot.software_requirements[0].name, "Ansys Mechanical APDL"
        )

        job_def = project_api.get_job_definitions(id=job.job_definition_id)[0]
        task_def = project_api.get_task_definitions(id=job_def.task_definition_ids[0])[0]
        max_eval_time = task_def.max_execution_time * 4
        job = self.wait_for_evaluation_of_job(project_api, job.id, max_eval_time)
        self.assertEqual(job.eval_status, "evaluated")

        # modify application of the process step
        task_def = project_api.get_task_definitions(id=job_def.task_definition_ids[0])[0]
        task_def.software_requirements[0].name = "NonExistingApp"
        task_def = project_api.update_task_definitions([task_def])[0]

        # the application in the task.task_definition_snapshot should not be modified
        project_api.sync_jobs([job])
        tasks = project_api.get_tasks(job_id=job.id)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].eval_status, "evaluated")
        self.assertEqual(
            tasks[0].task_definition_snapshot.software_requirements[0].name, "Ansys Mechanical APDL"
        )

        JmsApi(client).delete_project(project)

    def test_register_external_job(self):
        client = self.client

        jms_api = JmsApi(client)
        proj_name = f"test_register_external_job"
        proj = Project(name=proj_name, priority=1, active=True)
        proj = jms_api.create_project(proj)
        project_api = ProjectApi(client, proj.id)
        log.info(f"Created project '{proj.name}', ID='{proj.id}'")

        task_def = TaskDefinition(
            name="Fluent Session",
            software_requirements=[
                Software(name="Ansys Fluent Server", version="2023 R2"),
            ],
            execution_level=0,
            store_output=False,
        )

        task_def = project_api.create_task_definitions([task_def])[0]

        job_def = JobDefinition(name="JobDefinition", active=True)
        job_def.task_definition_ids = [task_def.id]
        job_def = project_api.create_job_definitions([job_def])[0]

        job = Job(
            name=f"Fluent Session",
            eval_status="running",
            job_definition_id=job_def.id,
        )
        job = project_api.create_jobs([job])[0]

        # add custom data to the task
        tasks = project_api.get_tasks(job_id=job.id)
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        self.assertEqual(task.eval_status, "running")

        task.custom_data = {"url": "http://localhost:5000", "some_other_data": "value"}
        project_api.update_tasks([task])

        tasks = project_api.get_tasks(job_id=job.id)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].custom_data["url"], "http://localhost:5000")
        self.assertEqual(tasks[0].eval_status, "running")

        JmsApi(client).delete_project(proj)


if __name__ == "__main__":
    unittest.main()
