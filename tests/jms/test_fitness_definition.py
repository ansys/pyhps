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

from marshmallow.utils import missing

from ansys.hps.client.jms import JmsApi, ProjectApi
from ansys.hps.client.jms.resource import JobDefinition, Project
from ansys.hps.client.jms.resource.fitness_definition import (
    FitnessDefinition,
    FitnessTermDefinition,
)
from ansys.hps.client.jms.schema.fitness_definition import (
    FitnessDefinitionSchema,
    FitnessTermDefinitionSchema,
)

log = logging.getLogger(__name__)


def test_fitness_definition_deserialization():
    fd_dict = {
        "obj_type": "FitnessDefinition",
        "error_fitness": 10.0,
        "fitness_term_definitions": [
            {
                "name": "eta",
                "expression": 'map_design_objective( values["P8"], 0.4, 0.6 )',
                "type": "design_objective",
                "weighting_factor": 0.1,
                "id": "02q3ThV29jVi0lsSI28DMt",
            },
            {
                "name": "Temp",
                "expression": 'map_limit_constraint( values["P17"], 680, 10 )',
                "type": "limit_constraint",
                "weighting_factor": 0.4,
                "id": "02q3Ti8zLWXUb2rqRYQbsh",
            },
            {
                "name": "Stiffness_Lateral",
                "expression": 'map_target_constraint(values["Stiffness_Lateral"], 45, 5, 10 )',
                "type": "target_constraint",
                "weighting_factor": 2.3,
                "id": "02q3TiMUsEwonhZofWQpwy",
            },
        ],
        "id": "02q3TiWeR58GmLPetRHZ45",
    }

    ftd_schema = FitnessTermDefinitionSchema()
    ftds = []
    for ftd_data in fd_dict["fitness_term_definitions"]:
        ftds.append(ftd_schema.load(ftd_data))

    for i, ftd in enumerate(ftds):
        assert ftd.__class__.__name__ == "FitnessTermDefinition"
        assert ftd.obj_type == "FitnessTermDefinition"
        assert ftd.id == fd_dict["fitness_term_definitions"][i]["id"]
        assert ftd.name == fd_dict["fitness_term_definitions"][i]["name"]
        assert ftd.expression == fd_dict["fitness_term_definitions"][i]["expression"]
        assert ftd.type == fd_dict["fitness_term_definitions"][i]["type"]
        assert ftd.weighting_factor == fd_dict["fitness_term_definitions"][i]["weighting_factor"]

    fd_schema = FitnessDefinitionSchema()
    fd = fd_schema.load(fd_dict)

    assert fd.__class__.__name__, "FitnessDefinition"
    assert fd.id == fd_dict["id"]
    assert fd.error_fitness == 10.0
    assert len(fd.fitness_term_definitions) == 3
    for i, ftd in enumerate(fd.fitness_term_definitions):
        assert ftd.obj_type == "FitnessTermDefinition"
        assert ftd.id == fd_dict["fitness_term_definitions"][i]["id"]
        assert ftd.name == fd_dict["fitness_term_definitions"][i]["name"]
        assert ftd.expression == fd_dict["fitness_term_definitions"][i]["expression"]
        assert ftd.type == fd_dict["fitness_term_definitions"][i]["type"]
        assert ftd.weighting_factor == fd_dict["fitness_term_definitions"][i]["weighting_factor"]


def test_fitness_definition_serialization():
    ftd = FitnessTermDefinition(name="ftd0", type="target_constraint", weighting_factor=0.1)

    assert ftd.expression == missing
    assert ftd.id == missing

    ftd_schema = FitnessTermDefinitionSchema()
    serialized_ftd = ftd_schema.dump(ftd)

    assert "expression" not in serialized_ftd.keys()
    assert "id" not in serialized_ftd.keys()
    assert serialized_ftd["name"] == "ftd0"
    assert serialized_ftd["type"] == "target_constraint"
    assert serialized_ftd["weighting_factor"] == 0.1

    fd = FitnessDefinition(error_fitness=3.14)
    assert fd.fitness_term_definitions == missing
    fd.fitness_term_definitions = [ftd]
    fd.add_fitness_term(name="ftd1", type="design_objective", weighting_factor=0.9)
    assert len(fd.fitness_term_definitions) == 2

    fd_schema = FitnessDefinitionSchema()
    serialized_fd = fd_schema.dump(fd)

    assert "id" not in serialized_fd.keys()
    assert serialized_fd["error_fitness"] == 3.14
    assert len(serialized_fd["fitness_term_definitions"]) == 2
    assert serialized_fd["fitness_term_definitions"][0]["type"] == "target_constraint"
    assert serialized_fd["fitness_term_definitions"][1]["type"] == "design_objective"


def test_fitness_definition_integration(client):
    proj_name = "test_jms_FitnessDefinitionTest"

    proj = Project(name=proj_name, active=True)
    jms_api = JmsApi(client)
    proj = jms_api.create_project(proj, replace=True)
    project_api = ProjectApi(client, proj.id)

    fd = FitnessDefinition(error_fitness=3.14)
    job_def = JobDefinition(name="New Config", active=True)
    job_def.fitness_definition = fd
    job_def = project_api.create_job_definitions([job_def])[0]
    assert job_def.fitness_definition.error_fitness == 3.14

    job_def.fitness_definition.add_fitness_term(
        name="test_ftd", type="design_objective", expression="0.0", weighting_factor=1.0
    )
    job_def = project_api.update_job_definitions([job_def])[0]
    assert job_def.fitness_definition.fitness_term_definitions[0].name == "test_ftd"
    assert job_def.fitness_definition.fitness_term_definitions[0].type == "design_objective"
    assert job_def.fitness_definition.fitness_term_definitions[0].expression == "0.0"

    job_def.fitness_definition.add_fitness_term(
        name="another_term", type="target_constraint", weighting_factor=0.2, expression="2.0"
    )
    job_def = project_api.update_job_definitions([job_def])[0]
    assert len(job_def.fitness_definition.fitness_term_definitions) == 2
    assert job_def.fitness_definition.fitness_term_definitions[1].name == "another_term"
    assert job_def.fitness_definition.fitness_term_definitions[1].type == "target_constraint"
    assert job_def.fitness_definition.fitness_term_definitions[1].expression == "2.0"
    assert job_def.fitness_definition.fitness_term_definitions[1].weighting_factor == 0.2

    # Delete project
    jms_api.delete_project(proj)
