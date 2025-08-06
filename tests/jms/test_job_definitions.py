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

import logging

from marshmallow.utils import missing

from ansys.hps.client import AuthApi, JmsApi, ProjectApi
from ansys.hps.client.jms.resource import (
    HpcResources,
    JobDefinition,
    Project,
    ResourceRequirements,
    TaskDefinition,
    WorkerContext,
)
from examples.mapdl_motorbike_frame.project_setup import create_project

log = logging.getLogger(__name__)


def test_job_definition_delete(client):
    proj_name = "rep_client_test_jms_JobDefinitionTest"

    proj = Project(name=proj_name, active=True)
    jms_api = JmsApi(client)
    proj = jms_api.create_project(proj, replace=True)
    project_api = ProjectApi(client, proj.id)

    job_def = JobDefinition(name="New Config", active=True)
    job_def = project_api.create_job_definitions([job_def])[0]

    assert len(project_api.get_job_definitions()) == 1

    project_api.delete_job_definitions([JobDefinition(id=job_def.id)])

    assert len(project_api.get_job_definitions()) == 0

    jms_api.delete_project(proj)


def test_task_definition_fields(client, has_hps_version_ge_1_3_45):
    # verify that:
    # - store_output is defaulted to True when undefined,
    # - memory and disk_space are correctly stored in bytes

    jms_api = JmsApi(client)
    proj_name = "test_store_output"

    project = Project(name=proj_name, active=False, priority=10)
    project = jms_api.create_project(project)
    project_api = ProjectApi(client, project.id)
    auth_api = AuthApi(client)

    task_def = TaskDefinition(
        name="Task.1",
        execution_command="%executable%",
        max_execution_time=10.0,
        execution_level=0,
        resource_requirements=ResourceRequirements(
            memory=256 * 1024 * 1024 * 1024,  # 256GB
            disk_space=2 * 1024 * 1024 * 1024 * 1024,  # 2TB
            hpc_resources=HpcResources(num_cores_per_node=2),
            compute_resource_set_id="abc123",
        ),
        worker_context=WorkerContext(max_runtime=3600, max_num_parallel_tasks=4),
        debug=True,
    )
    assert task_def.resource_requirements.hpc_resources.num_cores_per_node == 2

    task_def = project_api.create_task_definitions([task_def])[0]

    assert task_def.store_output
    assert task_def.resource_requirements.memory == 274877906944
    assert task_def.resource_requirements.disk_space == 2199023255552
    assert task_def.resource_requirements.hpc_resources.num_cores_per_node == 2
    assert task_def.worker_context.max_num_parallel_tasks == 4
    assert task_def.resource_requirements.compute_resource_set_id == "abc123"
    assert task_def.modified_by is not missing
    assert task_def.created_by is not missing

    if has_hps_version_ge_1_3_45:
        assert task_def.debug

    assert auth_api.get_user(id=task_def.created_by).username == client.username
    assert auth_api.get_user(id=task_def.modified_by).username == client.username

    jms_api.delete_project(project)


def test_task_and_job_definition_copy(client):
    # create new project
    num_jobs = 1
    project = create_project(
        client,
        "test_task_definition_copy",
        num_jobs=num_jobs,
        use_exec_script=False,
        active=False,
    )
    assert project is not None

    jms_api = JmsApi(client)
    project_api = ProjectApi(client, project.id)

    # copy task definition
    task_definitions = project_api.get_task_definitions()
    assert len(task_definitions) == 1

    original_td = task_definitions[0]
    new_td_id = project_api.copy_task_definitions(task_definitions)
    new_td = project_api.get_task_definitions(id=new_td_id)[0]

    assert original_td.name in new_td.name
    for attr in ["software_requirements", "resource_requirements", "execution_command"]:
        assert getattr(original_td, attr) == getattr(new_td, attr)

    # copy job definition
    job_definitions = project_api.get_job_definitions()
    assert len(job_definitions) == 1

    original_jd = job_definitions[0]
    new_jd_id = project_api.copy_job_definitions(job_definitions)
    new_jd = project_api.get_job_definitions(id=new_jd_id)[0]

    assert original_jd.name in new_jd.name
    assert len(original_jd.parameter_definition_ids) == len(new_jd.parameter_definition_ids)
    assert len(original_jd.parameter_mapping_ids) == len(new_jd.parameter_mapping_ids)
    assert len(original_jd.task_definition_ids) == len(new_jd.task_definition_ids)

    original_param_defs = project_api.get_parameter_definitions(
        id=original_jd.parameter_definition_ids
    )
    new_jd_param_defs = project_api.get_parameter_definitions(id=new_jd.parameter_definition_ids)
    for mode in ["input", "output"]:
        assert len([pd for pd in original_param_defs if pd.mode == mode]) == len(
            [pd for pd in new_jd_param_defs if pd.mode == mode]
        )

    jms_api.delete_project(project)
