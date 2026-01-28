# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

import logging

import pytest
from marshmallow.utils import missing

from ansys.hps.client import Client, ClientError
from ansys.hps.client.jms import JmsApi, ProjectApi
from ansys.hps.client.jms.resource import (
    FloatParameterDefinition,
    IntParameterDefinition,
    Job,
    JobDefinition,
    Project,
)
from examples.mapdl_motorbike_frame.project_setup import create_project

log = logging.getLogger(__name__)


def test_jms_api_info(client):
    jms_api = JmsApi(client)

    assert jms_api.url.endswith("/jms/api/v1")

    info = jms_api.get_api_info()
    assert "services" in info
    assert "build" in info
    assert "settings" in info
    assert "time" in info


def test_jms_api(client):
    log.debug("=== Client ===")
    proj_name = "Mapdl Motorbike Frame"

    log.debug("=== Projects ===")
    jms_api = JmsApi(client)

    assert jms_api._api_info is None
    _ = jms_api.get_api_info()
    assert jms_api._api_info is not None

    assert jms_api.version is not None

    project = jms_api.get_project_by_name(name=proj_name)

    if project:
        log.debug(f"Project: {project.id}")
        log.debug(f"project={project}")
    else:
        log.debug(f"Project {proj_name} not found. Creating it.")
        project = create_project(client, proj_name, num_jobs=5, use_exec_script=False)

    new_proj = Project(name="New project", active=True)
    new_proj = jms_api.create_project(new_proj, replace=True)
    # Delete project again
    jms_api.delete_project(new_proj)

    log.debug("=== JobDefinitions ===")
    project_api = ProjectApi(client, project.id)
    assert project_api.version == jms_api.version

    job_definitions = project_api.get_job_definitions(active=True)
    job_def = job_definitions[0]
    log.debug(f"job_definition={job_def}")

    log.debug("=== Jobs ===")
    all_jobs = project_api.get_jobs(fields="all", limit=50)
    log.debug(f"# jobs: {len(all_jobs)}")
    if all_jobs:
        log.debug(f"dp0={all_jobs[0]}")

    pending_jobs = project_api.get_jobs(eval_status="pending", limit=50)
    log.debug(f"Pending jobs: {[j.id for j in pending_jobs]}")

    # Alternative access with manually instantiated project
    proj = jms_api.get_projects(id=project.id)[0]
    project_api = ProjectApi(client, proj.id)
    evaluated_jobs = project_api.get_jobs(eval_status="evaluated", fields="all", limit=50)
    log.debug(f"Evaluated jobs: {[j.id for j in evaluated_jobs]}")

    # Access jobs data without objects
    dp_data = project_api.get_jobs(limit=3, as_objects=False)
    log.debug(f"dp_data={dp_data}")

    # Create some Jobs
    new_jobs = [
        Job(name=f"new_dp_{i}", eval_status="pending", job_definition_id=job_def.id)
        for i in range(10)
    ]
    created_jobs = project_api.create_jobs(new_jobs)

    # Delete Jobs again
    project_api.delete_jobs(created_jobs)


def test_fields_query_parameter(url, username, password):
    client1 = Client(url, username, password, all_fields=False)

    proj_name = "test_fields_query_parameter"
    project = create_project(client1, proj_name, num_jobs=2, use_exec_script=False)

    project_api1 = ProjectApi(client1, project.id)

    jobs = project_api1.get_jobs()
    assert len(jobs) == 2
    assert jobs[0].id != missing
    assert jobs[0].eval_status != missing
    assert jobs[0].values == missing
    assert jobs[0].host_ids == missing

    jobs = project_api1.get_jobs(fields=["id", "eval_status", "host_ids"])
    assert len(jobs) == 2
    assert jobs[0].id != missing
    assert jobs[0].eval_status != missing
    assert jobs[0].host_ids != missing
    assert jobs[0].values == missing

    client2 = Client(url, username, password, all_fields=True)
    project_api2 = ProjectApi(client2, project.id)

    jobs = project_api2.get_jobs()
    assert len(jobs) == 2
    assert jobs[0].id != missing
    assert jobs[0].eval_status != missing
    assert jobs[0].values != missing
    assert jobs[0].host_ids != missing

    jobs = project_api2.get_jobs(fields=["id", "eval_status"])
    assert len(jobs) == 2
    assert jobs[0].id != missing
    assert jobs[0].eval_status != missing
    assert jobs[0].host_ids == missing
    assert jobs[0].values == missing

    # Delete project
    JmsApi(client1).delete_project(project)


def test_storage_configuration(client):
    jms_api = JmsApi(client)
    storages = jms_api.get_storage()
    for storage in storages:
        assert "name" in storage
        assert "priority" in storage
        assert "obj_type" in storage


def test_objects_type_check(client):
    proj_name = "test_objects_type_check"

    proj = Project(name=proj_name, active=True)
    job_def = JobDefinition(name="Job Def", active=True)
    job = Job(name="test")

    jms_api = JmsApi(client)

    with pytest.raises(ClientError) as ex_info:
        _ = jms_api.create_task_definition_templates([job])
    assert "Wrong object type" in str(ex_info.value)
    assert "got <class 'ansys.hps.client.jms.resource.job.Job'>" in str(ex_info.value)

    proj = jms_api.create_project(proj, replace=True)
    project_api = ProjectApi(client, proj.id)

    job_def = JobDefinition(name="New Config", active=True)

    with pytest.raises(ClientError) as ex_info:
        _ = project_api.create_jobs([job_def])
    assert "Wrong object type" in str(ex_info.value)
    assert "got <class 'ansys.hps.client.jms.resource.job_definition.JobDefinition'>" in str(
        ex_info.value
    )

    job_def = project_api.create_job_definitions([job_def])[0]

    # verify support for mixed parameter definitions
    with pytest.raises(ClientError) as ex_info:
        _ = project_api.create_parameter_definitions(
            [
                FloatParameterDefinition(),
                Job(),
            ]
        )
    msg = str(ex_info.value)
    assert "Wrong object type" in msg
    assert "<class 'ansys.hps.client.jms.resource.job.Job'>" in msg
    assert (
        "<class 'ansys.hps.client.jms.resource.parameter_definition.FloatParameterDefinition'>"
        in msg
    )

    _ = project_api.create_parameter_definitions(
        [
            FloatParameterDefinition(),
            IntParameterDefinition(),
        ]
    )

    JmsApi(client).delete_project(proj)
