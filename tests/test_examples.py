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

import pytest

from ansys.hps.client import __ansys_apps_version__ as ansys_version
from ansys.hps.client.jms import (
    IntParameterDefinition,
    JmsApi,
    ProjectApi,
    StringParameterDefinition,
)

log = logging.getLogger(__name__)


def test_mapdl_motorbike_frame(client):
    from examples.mapdl_motorbike_frame.project_setup import create_project

    num_jobs = 5
    project = create_project(
        client, "Test mapdl_motorbike_frame", num_jobs=num_jobs, use_exec_script=False
    )
    assert project is not None

    jms_api = JmsApi(client)
    project_api = ProjectApi(client, project.id)

    assert len(project_api.get_jobs()) == num_jobs
    td = project_api.get_task_definitions()[0]
    assert len(td.success_criteria.required_output_file_ids) == 1

    jms_api.delete_project(project)


def test_mapdl_motorbike_frame_with_exec_script(client):
    from examples.mapdl_motorbike_frame.project_setup import create_project

    num_jobs = 5
    project = create_project(
        client, "Test mapdl_motorbike_frame", num_jobs=num_jobs, use_exec_script=True
    )
    assert project is not None

    jms_api = JmsApi(client)
    project_api = ProjectApi(client, project.id)

    assert len(project_api.get_jobs()) == num_jobs

    jms_api.delete_project(project)


def test_mapdl_motorbike_frame_with_user_defined_version(client):
    from examples.mapdl_motorbike_frame.project_setup import create_project

    num_jobs = 5
    project = create_project(
        client,
        "Test mapdl_motorbike_frame",
        version="2022 R1",
        num_jobs=num_jobs,
        use_exec_script=False,
    )
    assert project is not None

    jms_api = JmsApi(client)
    project_api = ProjectApi(client, project.id)

    assert len(project_api.get_jobs()) == num_jobs

    job_def = project_api.get_job_definitions()[0]
    task_def = project_api.get_task_definitions(id=job_def.task_definition_ids)[0]
    app = task_def.software_requirements[0]
    assert app.name == "Ansys Mechanical APDL"
    assert app.version == "2022 R1"

    jms_api.delete_project(project)


def test_mapdl_tyre_performance(client):
    from examples.mapdl_tyre_performance.project_setup import create_project

    num_jobs = 1
    project = create_project(client, "Test mapdl_tyre_performance", ansys_version, num_jobs)
    assert project is not None

    jms_api = JmsApi(client)
    project_api = ProjectApi(client, project.id)

    assert len(project_api.get_jobs()) == num_jobs

    jms_api.delete_project(project)


def test_python_two_bar_truss_problem(client):
    from examples.python_two_bar_truss_problem.project_setup import main

    num_jobs = 10
    project = main(client, num_jobs, use_exec_script=False)
    assert project is not None

    jms_api = JmsApi(client)
    project_api = ProjectApi(client, project.id)

    assert len(project_api.get_jobs()) == num_jobs

    jms_api.delete_project(project)


def test_python_two_bar_truss_problem_with_exec_script(client):
    from examples.python_two_bar_truss_problem.project_setup import main

    num_jobs = 10
    project = main(client, num_jobs, use_exec_script=True)
    assert project is not None

    jms_api = JmsApi(client)
    project_api = ProjectApi(client, project.id)

    assert len(project_api.get_jobs()) == num_jobs

    jms_api.delete_project(project)


def test_python_two_bar_truss_params_in_exec_script(client, has_hps_version_ge_1_3_45):
    if not has_hps_version_ge_1_3_45:
        pytest.skip("Returning output parameters in the execution script was added in HPS 1.3.45.")

    from examples.python_two_bar_truss_params_in_exec_script.project_setup import main

    num_jobs = 10
    project = main(client, num_jobs)
    assert project is not None

    jms_api = JmsApi(client)
    project_api = ProjectApi(client, project.id)

    assert len(project_api.get_jobs()) == num_jobs

    jms_api.delete_project(project)


def test_mapdl_linked_analyses(client):
    from examples.mapdl_linked_analyses.project_setup import create_project

    for incremental_version in [True, False]:
        project = create_project(
            client,
            name=f"Test linked analyses (incremental={incremental_version})",
            incremental=incremental_version,
            use_exec_script=False,
            version=ansys_version,
        )
        assert project is not None

        jms_api = JmsApi(client)
        project_api = ProjectApi(client, project.id)

        assert len(project_api.get_jobs()) == 1
        assert len(project_api.get_tasks()) == 3

        jms_api.delete_project(project)


def test_fluent_2d_heat_exchanger(client):
    from examples.fluent_2d_heat_exchanger.project_setup import create_project

    project = create_project(client, name="Fluent test (command)", version=ansys_version)
    assert project is not None

    jms_api = JmsApi(client)
    project_api = ProjectApi(client, project.id)

    assert len(project_api.get_jobs()) == 1
    assert jms_api.get_project(id=project.id).name == "Fluent test (command)"

    jms_api.delete_project(project)


def test_fluent_2d_heat_exchanger_with_exec_script(client):
    from examples.fluent_2d_heat_exchanger.project_setup import create_project

    project = create_project(
        client, name="Fluent test (exec script)", version=ansys_version, use_exec_script=True
    )
    assert project is not None

    jms_api = JmsApi(client)
    project_api = ProjectApi(client, project.id)

    assert len(project_api.get_jobs()) == 1
    assert jms_api.get_project(id=project.id).name == "Fluent test (exec script)"

    jms_api.delete_project(project)


def test_fluent_nozzle(client):
    from examples.fluent_nozzle.project_setup import create_project

    project = create_project(client, name="Fluent nozzle test", num_jobs=1, version=ansys_version)
    assert project is not None

    jms_api = JmsApi(client)
    project_api = ProjectApi(client, project.id)

    assert len(project_api.get_jobs()) == 1
    assert jms_api.get_project(id=project.id).name == "Fluent nozzle test"

    jms_api.delete_project(project)


def test_lsdyna_cylinder_plate(client):
    from examples.lsdyna_cylinder_plate.lsdyna_job import submit_job

    app_job = submit_job(
        client, name="LS-DYNA Cylinder Plate", version=ansys_version, use_exec_script=False
    )
    assert app_job is not None

    jms_api = JmsApi(client)
    project_api = ProjectApi(client, app_job.project_id)

    assert len(project_api.get_jobs()) == 1
    proj = jms_api.get_project(id=app_job.project_id)
    assert proj.name == "LS-DYNA Cylinder Plate"

    jms_api.delete_project(proj)


def test_lsdyna_cylinder_plate_with_exec_script(client, has_hps_version_ge_1_3_45):
    if not has_hps_version_ge_1_3_45:
        pytest.skip("LSDYNA execution script name is changed starting from HPS v1.3.45.")

    from examples.lsdyna_cylinder_plate.lsdyna_job import submit_job

    app_job = submit_job(client, name="LS-DYNA Cylinder Plate", version=ansys_version)
    assert app_job is not None

    jms_api = JmsApi(client)
    project_api = ProjectApi(client, app_job.project_id)

    assert len(project_api.get_jobs()) == 1
    proj = jms_api.get_project(id=app_job.project_id)
    assert proj.name == "LS-DYNA Cylinder Plate"

    jms_api.delete_project(proj)


def test_cfx_static_mixer(client):
    from examples.cfx_static_mixer.project_setup import create_project

    project = create_project(
        client, name="CFX static mixer test", num_jobs=1, version=ansys_version
    )
    assert project is not None

    jms_api = JmsApi(client)
    project_api = ProjectApi(client, project.id)

    assert len(project_api.get_jobs()) == 1
    assert jms_api.get_project(id=project.id).name == "CFX static mixer test"

    jms_api.delete_project(project)


def test_python_multi_steps(client):
    from examples.python_multi_process_step.project_setup import main as create_project

    num_jobs = 3
    num_task_definitions = 2
    project = create_project(
        client,
        num_task_definitions=num_task_definitions,
        num_jobs=num_jobs,
        duration=10,
        period=3,
        images=False,
        change_job_tasks=0,
        inactive=True,
        sequential=False,
    )
    assert project is not None

    project_api = ProjectApi(client, project.id)

    assert len(project_api.get_jobs()) == num_jobs

    # verify we created int and string type parameter definitions
    pds = project_api.get_parameter_definitions()
    types = [type(pd) for pd in pds]

    assert len(types) == 4 * num_task_definitions

    types = set(types)
    assert len(types) == 2
    assert StringParameterDefinition in types
    assert IntParameterDefinition in types

    JmsApi(client).delete_project(project)
