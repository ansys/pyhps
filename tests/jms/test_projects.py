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
import os
import tempfile
import time

import pytest
from ansys.hps.client import __ansys_apps_version__ as ansys_version
from ansys.hps.client.jms import JmsApi, ProjectApi
from ansys.hps.client.jms.resource import JobDefinition, LicenseContext, Project
from ansys.hps.client.jms.schema.project import ProjectSchema
from marshmallow.utils import missing

from examples.mapdl_motorbike_frame.project_setup import create_project as motorbike_create_project

log = logging.getLogger(__name__)


def test_project_deserialization():
    project_dict = {
        "name": "Fluent_2D_Cooling_mp",
        "active": False,
        "priority": 0,
        # "creation_time": "2019-05-28T11:37:23.361446+02:00",
        "statistics": {
            "eval_status": {
                "inactive": 1,
                "failed": 2,
                "timeout": 0,
                "aborted": 3,
                "pending": 0,
                "prolog": 8,
                "running": 9,
                "evaluated": 33,
            },
            "num_jobs": 56,
        },
    }

    project = ProjectSchema().load(project_dict)

    assert project.__class__.__name__ == "Project"
    assert project.creation_time == missing
    assert project.name == project_dict["name"]

    assert (
        project.statistics["eval_status"]["prolog"]
        == project_dict["statistics"]["eval_status"]["prolog"]
    )
    assert (
        project.statistics["eval_status"]["failed"]
        == project_dict["statistics"]["eval_status"]["failed"]
    )


def test_project_serialization():
    project = Project(name="new_project")

    assert project.creation_time == missing
    assert project.statistics == missing

    serialized_project = ProjectSchema().dump(project)

    assert "name" in serialized_project.keys()
    assert serialized_project["name"] == "new_project"


def test_project_integration(client):
    jms_api = JmsApi(client)
    proj_name = "test_jms_ProjectTest"

    proj = Project(name=proj_name, active=True, priority=10)
    proj = jms_api.create_project(proj, replace=True)

    proj = jms_api.get_project(id=proj.id)
    assert proj.creation_time is not None
    assert proj.priority == 10
    assert proj.active

    proj = jms_api.get_projects(name=proj.name, statistics=True)[0]
    assert proj.statistics["num_jobs"] == 0

    # statistics["eval_status"] might get few seconds until is populated on the server
    timeout = time.time() + 120
    while not proj.statistics["eval_status"] and time.time() < timeout:
        time.sleep(2)
        proj = jms_api.get_projects(id=proj.id, statistics=True)[0]
    assert proj.statistics["eval_status"]["prolog"] == 0
    assert proj.statistics["eval_status"]["failed"] == 0

    proj = jms_api.get_project(id=proj.id)
    proj.active = False
    proj = jms_api.update_project(proj)
    assert not proj.active

    # Delete project
    jms_api.delete_project(proj)


@pytest.mark.xfail
def test_project_replace(client):
    jms_api = JmsApi(client)

    p = Project(name="Original Project")
    p = jms_api.create_project(p)
    project_id = p.id
    p.name = "Replaced Project"
    p = jms_api.create_project(p, replace=True)

    assert p.id == project_id
    assert p.name == "Replaced Project"


def test_project_copy(client):
    jms_api = JmsApi(client)
    proj_name = "test_jms_ProjectCopyTest"

    proj = Project(name=proj_name, active=True, priority=10)
    proj = jms_api.create_project(proj, replace=True)

    project_api = ProjectApi(client, proj.id)
    proj1_id = project_api.copy_project()
    copied_proj1 = jms_api.get_project(id=proj1_id)
    assert copied_proj1 is not None
    assert copied_proj1.name == f"{proj.name} - copy"

    proj2_id = project_api.copy_project()
    copied_proj2 = jms_api.get_project(id=proj2_id)
    assert copied_proj2 is not None
    assert copied_proj2.name == f"{proj.name} - copy"

    # Delete projects
    jms_api.delete_project(copied_proj1)
    jms_api.delete_project(copied_proj2)
    jms_api.delete_project(proj)


@pytest.mark.xfail
def test_project_license_context(client):
    jms_api = JmsApi(client)
    proj_name = "test_jms_ProjectTest_license_context"

    proj = Project(id=proj_name, active=True, priority=10)
    proj = jms_api.create_project(proj, replace=True)
    project_api = ProjectApi(client, proj.id)

    # Create new license context in JMS
    license_contexts = project_api.create_license_contexts()
    assert len(license_contexts) == 1
    assert len(license_contexts[0].context_id) > 0
    assert len(license_contexts[0].environment) == 2

    license_contexts = project_api.get_license_contexts()
    assert len(license_contexts) == 1
    assert len(license_contexts[0].context_id) > 0
    assert len(license_contexts[0].environment) == 2

    # Terminate license context
    project_api.delete_license_contexts()
    license_contexts = project_api.get_license_contexts()
    assert len(license_contexts) == 0

    # Set a license context from outside=
    lc = LicenseContext(
        environment={
            "ANSYS_HPC_PARAMETRIC_ID": "my_id",
            "ANSYS_HPC_PARAMETRIC_SERVER": "my_server",
        }
    )
    license_contexts = project_api.update_license_contexts([lc])
    assert len(license_contexts) == 1
    assert license_contexts[0].context_id == "my_id"
    assert len(license_contexts[0].environment) == 2
    assert license_contexts[0].environment["ANSYS_HPC_PARAMETRIC_ID"] == "my_id"
    assert license_contexts[0].environment["ANSYS_HPC_PARAMETRIC_SERVER"] == "my_server"

    license_contexts = project_api.get_license_contexts()
    assert len(license_contexts) == 1
    assert license_contexts[0].context_id == "my_id"
    assert len(license_contexts[0].environment) == 2
    assert license_contexts[0].environment["ANSYS_HPC_PARAMETRIC_ID"] == "my_id"
    assert license_contexts[0].environment["ANSYS_HPC_PARAMETRIC_SERVER"] == "my_server"

    # Remove the license context set from outside again
    project_api.delete_license_contexts()
    license_contexts = project_api.get_license_contexts()
    assert len(license_contexts) == 0

    # Delete project
    jms_api.delete_project(proj)


def test_project_delete_job_definition(client):
    jms_api = JmsApi(client)
    proj_name = "test_jms_ProjectTest_delete_config"

    proj = Project(name=proj_name, active=True, priority=10)
    proj = jms_api.create_project(proj, replace=True)

    project_api = ProjectApi(client, proj.id)

    job_def = JobDefinition(name="Config1")
    job_def = project_api.create_job_definitions([job_def])[0]
    assert len(project_api.get_job_definitions()) == 1
    project_api.delete_job_definitions([job_def])
    assert len(project_api.get_job_definitions()) == 0

    jms_api.delete_project(proj)


def test_project_archive_restore(client):
    num_jobs = 2
    jms_api = JmsApi(client)
    proj_name = "test_jms_project_archive_restore"

    # Setup project to work with
    project = motorbike_create_project(client=client, name=proj_name, num_jobs=num_jobs)
    project.active = False
    project.priority = 6
    project = jms_api.update_project(project)

    restored_project = None
    project_api = ProjectApi(client, project.id)
    with tempfile.TemporaryDirectory() as tpath:
        # Archive project
        archive_path = project_api.archive_project(tpath, include_job_files=True)
        assert os.path.exists(archive_path)
        log.info(f"Archive size {os.path.getsize(archive_path)} bytes")
        assert os.path.getsize(archive_path) > 2e3  # file larger than 2 KB size

        # Restore project
        restored_project = jms_api.restore_project(archive_path)
        restored_project_api = ProjectApi(client, restored_project.id)

        assert not restored_project.active
        assert restored_project.priority == 6
        assert len(project_api.get_job_definitions()) == len(
            restored_project_api.get_job_definitions()
        )
        assert len(project_api.get_jobs()) == len(restored_project_api.get_jobs())

    jms_api.delete_project(project)
    jms_api.delete_project(restored_project)


def test_copy_exec_script(client):
    jms_api = JmsApi(client)
    proj_name = "test_copy_exec_script"

    proj = Project(name=proj_name)
    proj = jms_api.create_project(proj)

    project_api = ProjectApi(client, proj.id)

    ansys_short_version = f"v{ansys_version[2:4]}{ansys_version[6]}"
    script_names = [f"mapdl-{ansys_short_version}-exec_mapdl", "mechanical-exec_mechanical"]

    for script_name in script_names:
        file = project_api.copy_default_execution_script(f"{script_name}.py")
        assert file.name == script_name
        assert file.evaluation_path == f"{script_name}.py"
        assert file.hash is not None
        assert file.storage_id is not None

    jms_api.delete_project(proj)
