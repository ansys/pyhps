# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------
import copy
import logging
import unittest
import uuid

from examples.mapdl_motorbike_frame.project_setup import create_project
from marshmallow.utils import missing

from ansys.rep.client.jms import JmsApi, ProjectApi
from ansys.rep.client.jms.resource import Job, JobDefinition, Project
from ansys.rep.client.jms.schema.job import JobSchema
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class JobsTest(REPTestCase):
    def test_job_deserialization(self):

        dp_dict = {
            "id": "02q1DiPEP0nanLN5384q8L",
            "obj_type": "Job",
            "modification_time": "2021-03-03T19:39:38.826286+00:00",
            "creation_time": "2021-03-03T19:38:15.024782+00:00",
            "name": "Job.0",
            "job_definition_id": "02q3QL54xZzmBhfkAcEdqh",
            "eval_status": "evaluated",
            "priority": 0,
            "fitness": 0.2344,
            "fitness_term_values": {"fit_term1": 1.5},
            "note": "hello",
            "creator": "Creator.1",
            "executed_task_definition_level": 0,
            "values": {
                "tube1_radius": 12.509928919324276,
                "tube1_thickness": 0.588977941435834,
                "tube2_radius": 18.945561281799783,
                "tube2_thickness": 2.3025575742140045,
                "tube3_radius": 8.924275302529148,
                "tube3_thickness": 1.203142161159792,
                "weight": 6.89853756,
                "torsion_stiffness": 1507.29699128,
                "max_stress": 333.69761428,
                "mapdl_elapsed_time_obtain_license": 1.5,
                "mapdl_cp_time": 0.609,
                "mapdl_elapsed_time": 3.0,
                "tube1": "1",
                "tube2": "3",
                "tube3": "2",
            },
            "elapsed_time": 14.922003,
            "evaluators": ["9be2d91a-abb1-3b68-bc36-d23a990a9792"],
            "file_ids": [
                "02q3QVM1RJMzSKccWZ5gUT",
                "02q3QKzo7389RU5tGfDhPj",
                "02q3QVs2PuyRm354BhQ1NC",
                "02q3QVs2XWGzYEiziMrjK0",
                "02q3QVM1TVf90w7MLI36jJ",
                "02q3QVM1W9pTrKUcLCQZyN",
            ],
        }

        schema = JobSchema()
        job = schema.load(dp_dict)
        self.assertEqual(job.id, "02q1DiPEP0nanLN5384q8L")
        self.assertEqual(job.name, "Job.0")
        self.assertEqual(job.job_definition_id, "02q3QL54xZzmBhfkAcEdqh")
        self.assertEqual(job.eval_status, "evaluated")
        self.assertEqual(job.priority, 0)
        self.assertAlmostEqual(job.fitness, 0.2344)
        self.assertEqual(job.fitness_term_values["fit_term1"], 1.5)

        self.assertEqual(job.note, "hello")
        self.assertEqual(job.creator, "Creator.1")
        self.assertEqual(job.executed_task_definition_level, 0)
        self.assertEqual(len(job.values), 15)
        self.assertAlmostEqual(job.values["tube1_radius"], 12.509928919324276)
        self.assertAlmostEqual(job.values["mapdl_elapsed_time"], 3.0)
        self.assertEqual(job.values["tube1"], "1")

        self.assertAlmostEqual(job.elapsed_time, 14.922003)
        self.assertEqual(job.evaluators, ["9be2d91a-abb1-3b68-bc36-d23a990a9792"])
        self.assertEqual(
            job.file_ids,
            [
                "02q3QVM1RJMzSKccWZ5gUT",
                "02q3QKzo7389RU5tGfDhPj",
                "02q3QVs2PuyRm354BhQ1NC",
                "02q3QVs2XWGzYEiziMrjK0",
                "02q3QVM1TVf90w7MLI36jJ",
                "02q3QVM1W9pTrKUcLCQZyN",
            ],
        )

    def test_job_serialization(self):

        job = Job(
            name="dp0",
            job_definition_id=2,
            evaluators=["uuid-4", "uuid-5"],
            values={"p1": "string_value", "p2": 8.9, "p3": True},
            creator="dcs-client",
            elapsed_time=40.8,
        )

        self.assertEqual(job.note, missing)
        self.assertEqual(job.priority, missing)
        self.assertEqual(job.elapsed_time, 40.8)

        schema = JobSchema()
        serialized_job = schema.dump(job)

        self.assertFalse("elapsed_time" in serialized_job.keys())
        self.assertEqual(serialized_job["values"]["p1"], "string_value")
        self.assertEqual(serialized_job["values"]["p2"], 8.9)
        self.assertEqual(serialized_job["values"]["p3"], True)
        self.assertFalse("fitness" in serialized_job.keys())
        self.assertFalse("files" in serialized_job.keys())
        self.assertEqual(len(serialized_job["evaluators"]), 2)
        self.assertEqual(serialized_job["evaluators"][1], "uuid-5")

    def test_job_integration(self):

        client = self.client()
        proj_name = f"dcs_client_test_jobs_JobTest_{self.run_id}"

        proj = Project(name=proj_name, active=True)
        jms_api = JmsApi(client)
        proj = jms_api.create_project(proj, replace=True)
        project_api = ProjectApi(client, proj.id)

        job_def = JobDefinition(name="New Config", active=True)
        job_def = project_api.create_job_definitions([job_def])[0]

        # test creating, update and delete with no jobs
        jobs = project_api.create_jobs([])
        self.assertEqual(len(jobs), 0)
        jobs = project_api.create_jobs([], as_objects=True)
        self.assertEqual(len(jobs), 0)
        jobs = project_api.update_jobs([])
        self.assertEqual(len(jobs), 0)
        jobs = project_api.update_jobs([], as_objects=True)
        self.assertEqual(len(jobs), 0)
        project_api.delete_jobs([])

        jobs = [
            Job(name=f"dp_{i}", eval_status="inactive", job_definition_id=job_def.id)
            for i in range(10)
        ]
        jobs = project_api.create_jobs(jobs)
        for job in jobs:
            # check that all fields are populated (i.e. request params include fields="all")
            self.assertEqual(job.creator, None)
            self.assertEqual(job.note, None)
            self.assertEqual(job.fitness, None)
            self.assertTrue(job.executed_task_definition_level is not None)

        jobs = project_api.get_jobs()
        for job in jobs:
            # check that all fields are populated (i.e. request params include fields="all")
            self.assertEqual(job.creator, None)
            self.assertEqual(job.note, None)
            self.assertEqual(job.fitness, None)
            self.assertTrue(job.executed_task_definition_level is not None)
            # fill some of them
            job.creator = "rep-client"
            job.note = f"test job{job.id} update"

        jobs = project_api.update_jobs(jobs)
        for job in jobs:
            # check that all fields are populated (i.e. request params include fields="all")
            self.assertTrue(job.creator is not None)
            self.assertTrue(job.note is not None)
            self.assertTrue(job.job_definition_id, 1)
            self.assertEqual(job.fitness, None)
            self.assertTrue(job.executed_task_definition_level is not None)

        jobs = project_api.get_jobs(limit=2, fields=["id", "creator", "note"])

        self.assertEqual(len(jobs), 2)
        for job in jobs:
            self.assertEqual(job.creator, "rep-client")
            self.assertEqual(job.note, f"test job{job.id} update")
            self.assertEqual(job.job_definition_id, missing)

        project_api.delete_jobs([Job(id=job.id) for job in jobs])
        jobs = project_api.get_jobs()
        self.assertEqual(len(jobs), 8)

        new_jobs = project_api.copy_jobs([Job(id=job.id) for job in jobs[:3]])
        for i in range(3):
            self.assertEqual(new_jobs[i].creator, jobs[i].creator)
            self.assertEqual(new_jobs[i].note, jobs[i].note)
            self.assertEqual(new_jobs[i].job_definition_id, jobs[i].job_definition_id)
        all_jobs = project_api.get_jobs()
        self.assertEqual(len(all_jobs), len(jobs) + len(new_jobs))

        # Delete project
        jms_api.delete_project(proj)

    def test_job_update(self):
        client = self.client()
        jms_api = JmsApi(client)
        proj_name = f"test_job_update_{uuid.uuid4().hex[:8]}"

        project = create_project(client=client, name=proj_name, num_jobs=2)
        project.active = False
        project = jms_api.update_project(project)
        project_api = ProjectApi(client, project.id)

        job_def = project_api.get_job_definitions()[0]
        params = project_api.get_parameter_definitions(id=job_def.parameter_definition_ids)
        input_parameters = [p.name for p in params if p.mode == "input"]

        jobs = project_api.get_jobs(fields="all")
        ref_values = {job.id: copy.deepcopy(job.values) for job in jobs}

        # change eval status with full DP object
        for job in jobs:
            job.eval_status = "pending"
        jobs = project_api.update_jobs(jobs)

        for job in jobs:
            for p_name in input_parameters:
                self.assertEqual(job.values[p_name], ref_values[job.id][p_name])

        # change eval status with minimal DP object
        jobs = project_api.get_jobs(fields=["id", "eval_status"])
        for job in jobs:
            job.eval_status = "pending"
        jobs = project_api.update_jobs(jobs)

        for job in jobs:
            for p_name in input_parameters:
                self.assertEqual(job.values[p_name], ref_values[job.id][p_name])

        # change eval status with partial DP object including config id
        jobs = project_api.get_jobs(fields=["id", "job_definition_id", "eval_status"])
        for job in jobs:
            job.eval_status = "pending"
        jobs = project_api.update_jobs(jobs)

        for job in jobs:
            for p_name in input_parameters:
                self.assertEqual(job.values[p_name], ref_values[job.id][p_name], p_name)

        jms_api.delete_project(project)


if __name__ == "__main__":
    unittest.main()
