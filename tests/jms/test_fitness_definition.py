# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------
import logging
import unittest

from marshmallow.utils import missing

from ansys.rep.client.jms import JmsApi, ProjectApi
from ansys.rep.client.jms.resource import JobDefinition, Project
from ansys.rep.client.jms.resource.fitness_definition import (
    FitnessDefinition,
    FitnessTermDefinition,
)
from ansys.rep.client.jms.schema.fitness_definition import (
    FitnessDefinitionSchema,
    FitnessTermDefinitionSchema,
)
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class FitnessDefitionTest(REPTestCase):
    def test_fitness_definition_deserialization(self):

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
            self.assertEqual(ftd.__class__.__name__, "FitnessTermDefinition")
            self.assertEqual(ftd.obj_type, "FitnessTermDefinition")
            self.assertEqual(ftd.id, fd_dict["fitness_term_definitions"][i]["id"])
            self.assertEqual(ftd.name, fd_dict["fitness_term_definitions"][i]["name"])
            self.assertEqual(ftd.expression, fd_dict["fitness_term_definitions"][i]["expression"])
            self.assertEqual(ftd.type, fd_dict["fitness_term_definitions"][i]["type"])
            self.assertEqual(
                ftd.weighting_factor, fd_dict["fitness_term_definitions"][i]["weighting_factor"]
            )

        fd_schema = FitnessDefinitionSchema()
        fd = fd_schema.load(fd_dict)

        self.assertEqual(fd.__class__.__name__, "FitnessDefinition")
        self.assertEqual(fd.id, fd_dict["id"])
        self.assertEqual(fd.error_fitness, 10.0)
        self.assertEqual(len(fd.fitness_term_definitions), 3)
        for i, ftd in enumerate(fd.fitness_term_definitions):
            self.assertEqual(ftd.obj_type, "FitnessTermDefinition")
            self.assertEqual(ftd.id, fd_dict["fitness_term_definitions"][i]["id"])
            self.assertEqual(ftd.name, fd_dict["fitness_term_definitions"][i]["name"])
            self.assertEqual(ftd.expression, fd_dict["fitness_term_definitions"][i]["expression"])
            self.assertEqual(ftd.type, fd_dict["fitness_term_definitions"][i]["type"])
            self.assertEqual(
                ftd.weighting_factor, fd_dict["fitness_term_definitions"][i]["weighting_factor"]
            )

    def test_fitness_definition_serialization(self):

        ftd = FitnessTermDefinition(name="ftd0", type="target_constraint", weighting_factor=0.1)

        self.assertEqual(ftd.expression, missing)
        self.assertEqual(ftd.id, missing)

        ftd_schema = FitnessTermDefinitionSchema()
        serialized_ftd = ftd_schema.dump(ftd)

        self.assertFalse("expression" in serialized_ftd.keys())
        self.assertFalse("id" in serialized_ftd.keys())
        self.assertEqual(serialized_ftd["name"], "ftd0")
        self.assertEqual(serialized_ftd["type"], "target_constraint")
        self.assertEqual(serialized_ftd["weighting_factor"], 0.1)

        fd = FitnessDefinition(error_fitness=3.14)
        self.assertEqual(fd.fitness_term_definitions, missing)
        fd.fitness_term_definitions = [ftd]
        fd.add_fitness_term(name="ftd1", type="design_objective", weighting_factor=0.9)
        self.assertEqual(len(fd.fitness_term_definitions), 2)

        fd_schema = FitnessDefinitionSchema()
        serialized_fd = fd_schema.dump(fd)

        self.assertFalse("id" in serialized_fd.keys())
        self.assertEqual(serialized_fd["error_fitness"], 3.14)
        self.assertEqual(len(serialized_fd["fitness_term_definitions"]), 2)
        self.assertEqual(serialized_fd["fitness_term_definitions"][0]["type"], "target_constraint")
        self.assertEqual(serialized_fd["fitness_term_definitions"][1]["type"], "design_objective")

    def test_fitness_definition_integration(self):

        client = self.client()
        proj_name = f"test_dps_FitnessDefinitionTest_{self.run_id}"

        proj = Project(name=proj_name, active=True)
        jms_api = JmsApi(client)
        proj = jms_api.create_project(proj, replace=True)
        project_api = ProjectApi(client, proj.id)

        fd = FitnessDefinition(error_fitness=3.14)
        job_def = JobDefinition(name="New Config", active=True)
        job_def.fitness_definition = fd
        job_def = project_api.create_job_definitions([job_def])[0]
        self.assertEqual(job_def.fitness_definition.error_fitness, 3.14)

        job_def.fitness_definition.add_fitness_term(
            name="test_ftd", type="design_objective", expression="0.0", weighting_factor=1.0
        )
        job_def = project_api.update_job_definitions([job_def])[0]
        self.assertEqual(job_def.fitness_definition.fitness_term_definitions[0].name, "test_ftd")
        self.assertEqual(
            job_def.fitness_definition.fitness_term_definitions[0].type, "design_objective"
        )
        self.assertEqual(job_def.fitness_definition.fitness_term_definitions[0].expression, "0.0")

        job_def.fitness_definition.add_fitness_term(
            name="another_term", type="target_constraint", weighting_factor=0.2, expression="2.0"
        )
        job_def = project_api.update_job_definitions([job_def])[0]
        self.assertEqual(len(job_def.fitness_definition.fitness_term_definitions), 2)
        self.assertEqual(
            job_def.fitness_definition.fitness_term_definitions[1].name, "another_term"
        )
        self.assertEqual(
            job_def.fitness_definition.fitness_term_definitions[1].type, "target_constraint"
        )
        self.assertEqual(job_def.fitness_definition.fitness_term_definitions[1].expression, "2.0")
        self.assertEqual(
            job_def.fitness_definition.fitness_term_definitions[1].weighting_factor, 0.2
        )

        # Delete project
        jms_api.delete_project(proj)


if __name__ == "__main__":
    unittest.main()
