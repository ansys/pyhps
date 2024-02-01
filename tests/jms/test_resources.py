# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
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

from examples.mapdl_motorbike_frame.project_setup import create_project
from marshmallow import missing

from ansys.hps.client.jms import (
    FitnessDefinition,
    JmsApi,
    JobDefinition,
    ProjectApi,
    ResourceRequirements,
    Software,
    TaskDefinition,
)

log = logging.getLogger(__name__)


def test_task_definition_equality():

    td1 = TaskDefinition(
        name="TD.1",
        execution_command="%executable%",
        max_execution_time=10.0,
        execution_level=0,
        resource_requirements=ResourceRequirements(
            memory=256,
            disk_space=2,
        ),
        software_requirements=Software(name="app", version="0.1"),
    )

    assert td1 != None
    assert None != td1
    assert None != td1

    td2 = TaskDefinition(
        name="TD.1",
        execution_command="%executable%",
        max_execution_time=10.0,
        execution_level=0,
        resource_requirements=ResourceRequirements(
            memory=256,
            disk_space=2,
        ),
        software_requirements=Software(name="app", version="0.1"),
    )

    td3 = td2

    assert not td1 is td2
    assert td3 is td2
    assert td1 == td2
    assert td2 == td1
    assert td1 == td3

    td2.environment = None
    assert td1.environment == missing
    assert not td1 == td2
    assert not td2 == td1

    td1.environment = None
    assert td1 == td2
    assert td2 == td1

    jd = JobDefinition()
    td = TaskDefinition()
    assert not jd == td


def test_job_definitions_equality():

    fd1 = FitnessDefinition(error_fitness=10.0)
    fd1.add_fitness_term(
        name="weight",
        type="design_objective",
        weighting_factor=1.0,
        expression="map_design_objective( values['weight'], 7.5, 5.5)",
    )
    fd1.add_fitness_term(
        name="torsional_stiffness",
        type="target_constraint",
        weighting_factor=1.0,
        expression="map_target_constraint( values['torsion_stiffness'], 1313.0, 5.0, 30.0 )",
    )

    jd1 = JobDefinition(fitness_definition=fd1)

    fd2 = FitnessDefinition(error_fitness=10.0)
    fd2.add_fitness_term(
        name="weight",
        type="design_objective",
        weighting_factor=1.0,
        expression="map_design_objective( values['weight'], 7.5, 5.5)",
    )
    fd2.add_fitness_term(
        name="torsional_stiffness",
        type="target_constraint",
        weighting_factor=1.0,
        expression="map_target_constraint( values['torsion_stiffness'], 1313.0, 5.0, 30.0 )",
    )
    jd2 = JobDefinition(fitness_definition=fd2)

    assert jd1 == jd2
    assert not jd1 is jd2

    jd2.fitness_definition.fitness_term_definitions[0].expression = "_changed_"

    assert jd1 != jd2
    assert jd2 != jd1


def test_jobs_equality(client):

    # create new project
    num_jobs = 1
    project = create_project(
        client,
        f"test_jobs_equality",
        num_jobs=num_jobs,
        use_exec_script=False,
        active=False,
    )
    assert project is not None

    project_api = ProjectApi(client, project.id)

    job1 = project_api.get_jobs(limit=1)[0]
    job_id = job1.id

    job2 = project_api.get_jobs(id=job_id)[0]
    assert job1 == job2

    job2 = project_api.get_jobs(id=job_id, fields=["id", "name"])[0]
    assert job1 != job2

    jms_api = JmsApi(client)
    jms_api.delete_project(project)
