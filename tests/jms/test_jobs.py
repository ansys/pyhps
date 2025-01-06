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

import copy
import logging
import uuid

from examples.mapdl_motorbike_frame.project_setup import create_project
from marshmallow.utils import missing
import pytest

from ansys.hps.client import AuthApi, JmsApi, ProjectApi
from ansys.hps.client.jms.resource import Job, JobDefinition, Project
from ansys.hps.client.jms.schema.job import JobSchema

log = logging.getLogger(__name__)


def test_job_deserialization():

    job_dict = {
        "id": "02q1DiPEP0nanLN5384q8L",
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
        "executed_level": 0,
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
        "host_ids": ["9be2d91a-abb1-3b68-bc36-d23a990a9792"],
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
    job = schema.load(job_dict)
    assert job.id == "02q1DiPEP0nanLN5384q8L"
    assert job.name == "Job.0"
    assert job.job_definition_id == "02q3QL54xZzmBhfkAcEdqh"
    assert job.eval_status == "evaluated"
    assert job.priority == 0
    assert job.fitness == pytest.approx(0.2344)
    assert job.fitness_term_values["fit_term1"] == 1.5

    assert job.note == "hello"
    assert job.creator == "Creator.1"
    assert job.executed_level == 0
    assert len(job.values) == 15
    assert job.values["tube1_radius"] == pytest.approx(12.509928919324276)
    assert job.values["mapdl_elapsed_time"] == pytest.approx(3.0)
    assert job.values["tube1"] == "1"

    assert job.elapsed_time == pytest.approx(14.922003)
    assert job.host_ids == ["9be2d91a-abb1-3b68-bc36-d23a990a9792"]
    assert job.file_ids == [
        "02q3QVM1RJMzSKccWZ5gUT",
        "02q3QKzo7389RU5tGfDhPj",
        "02q3QVs2PuyRm354BhQ1NC",
        "02q3QVs2XWGzYEiziMrjK0",
        "02q3QVM1TVf90w7MLI36jJ",
        "02q3QVM1W9pTrKUcLCQZyN",
    ]


def test_job_serialization():

    job = Job(
        name="dp0",
        job_definition_id=2,
        host_ids=["uuid-4", "uuid-5"],
        values={"p1": "string_value", "p2": 8.9, "p3": True},
        creator="hps-client",
        elapsed_time=40.8,
    )

    assert job.note == missing
    assert job.priority == missing
    assert job.elapsed_time == 40.8
    assert job.creator == "hps-client"

    schema = JobSchema()
    serialized_job = schema.dump(job)

    assert not "elapsed_time" in serialized_job.keys()
    assert serialized_job["values"]["p1"] == "string_value"
    assert serialized_job["values"]["p2"] == 8.9
    assert serialized_job["values"]["p3"] == True
    assert not "fitness" in serialized_job.keys()
    assert not "files" in serialized_job.keys()
    assert len(serialized_job["host_ids"]) == 2
    assert serialized_job["host_ids"][1] == "uuid-5"


def test_job_integration(client):

    proj_name = f"test_jobs_JobTest"

    proj = Project(name=proj_name, active=True)
    jms_api = JmsApi(client)
    proj = jms_api.create_project(proj, replace=True)
    project_api = ProjectApi(client, proj.id)

    job_def = JobDefinition(name="New Config", active=True)
    job_def = project_api.create_job_definitions([job_def])[0]

    assert job_def.modified_by is not missing
    assert job_def.created_by is not missing

    # test creating, update and delete with no jobs
    jobs = project_api.create_jobs([])
    assert len(jobs) == 0
    jobs = project_api.create_jobs([], as_objects=True)
    assert len(jobs) == 0
    jobs = project_api.update_jobs([])
    assert len(jobs) == 0
    jobs = project_api.update_jobs([], as_objects=True)
    assert len(jobs) == 0
    project_api.delete_jobs([])

    jobs = [
        Job(name=f"dp_{i}", eval_status="inactive", job_definition_id=job_def.id) for i in range(10)
    ]
    jobs = project_api.create_jobs(jobs)
    for job in jobs:
        # check that all fields are populated (i.e. request params include fields="all")
        assert job.creator == None
        assert job.note == None
        assert job.fitness == None
        assert job.executed_level is not None
        assert job.modified_by is not missing
        assert job.created_by is not missing

    jobs = project_api.get_jobs()
    auth_api = AuthApi(client)
    for job in jobs:
        # check that all fields are populated (i.e. request params include fields="all")
        assert job.creator == None
        assert job.note == None
        assert job.fitness == None
        assert job.executed_level is not None
        assert job.modified_by is not missing
        assert job.created_by is not missing
        assert auth_api.get_user(id=job.created_by).username == client.username
        assert auth_api.get_user(id=job.modified_by).username == client.username
        # fill some of them
        job.creator = "hps-client"
        job.note = f"test job{job.id} update"

    jobs = project_api.update_jobs(jobs)
    for job in jobs:
        # check that all fields are populated (i.e. request params include fields="all")
        assert job.creator is not None
        assert job.note is not None
        assert job.job_definition_id, 1
        assert job.fitness == None
        assert job.executed_level is not None

    jobs = project_api.get_jobs(limit=2, fields=["id", "creator", "note"])

    assert len(jobs) == 2
    for job in jobs:
        assert job.creator == "hps-client"
        assert job.note == f"test job{job.id} update"
        assert job.job_definition_id == missing

    project_api.delete_jobs([Job(id=job.id) for job in jobs])
    jobs = project_api.get_jobs()
    assert len(jobs) == 8

    new_job_ids = project_api.copy_jobs([Job(id=job.id) for job in jobs[:3]])
    new_jobs = project_api.get_jobs(id=new_job_ids)
    for i in range(3):
        assert new_jobs[i].creator == jobs[i].creator
        assert new_jobs[i].note == jobs[i].note
        assert new_jobs[i].job_definition_id == jobs[i].job_definition_id
    all_jobs = project_api.get_jobs()
    assert len(all_jobs) == len(jobs) + len(new_jobs)

    # Delete project
    jms_api.delete_project(proj)


def test_job_update(client):
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
            assert job.values[p_name] == ref_values[job.id][p_name]

    # change eval status with minimal DP object
    jobs = project_api.get_jobs(fields=["id", "eval_status"])
    for job in jobs:
        job.eval_status = "pending"
    jobs = project_api.update_jobs(jobs)

    for job in jobs:
        for p_name in input_parameters:
            assert job.values[p_name] == ref_values[job.id][p_name]

    # change eval status with partial DP object including config id
    jobs = project_api.get_jobs(fields=["id", "job_definition_id", "eval_status"])
    for job in jobs:
        job.eval_status = "pending"
    jobs = project_api.update_jobs(jobs)

    for job in jobs:
        for p_name in input_parameters:
            assert job.values[p_name] == ref_values[job.id][p_name], p_name

    jms_api.delete_project(project)
