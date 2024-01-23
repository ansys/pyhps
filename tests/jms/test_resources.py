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
import unittest

from examples.mapdl_motorbike_frame.project_setup import create_project
from marshmallow import missing

from ansys.hps.core.jms import (
    FitnessDefinition,
    JmsApi,
    JobDefinition,
    ProjectApi,
    ResourceRequirements,
    Software,
    TaskDefinition,
)
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class REPClientTest(REPTestCase):
    def test_task_definition_equality(self):

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

        self.assertTrue(td1 != None)
        self.assertTrue(None != td1)
        self.assertTrue(None != td1)

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

        self.assertFalse(td1 is td2)
        self.assertTrue(td3 is td2)
        self.assertTrue(td1 == td2)
        self.assertTrue(td2 == td1)
        self.assertTrue(td1 == td3)

        td2.environment = None
        self.assertTrue(td1.environment == missing)
        self.assertFalse(td1 == td2)
        self.assertFalse(td2 == td1)

        td1.environment = None
        self.assertTrue(td1 == td2)
        self.assertTrue(td2 == td1)

        jd = JobDefinition()
        td = TaskDefinition()
        self.assertFalse(jd == td)

    def test_job_definitions_equality(self):

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

        self.assertTrue(jd1 == jd2)
        self.assertFalse(jd1 is jd2)

        jd2.fitness_definition.fitness_term_definitions[0].expression = "_changed_"

        self.assertTrue(jd1 != jd2)
        self.assertTrue(jd2 != jd1)

    def test_jobs_equality(self):

        # create new project
        num_jobs = 1
        project = create_project(
            self.client,
            f"test_jobs_equality",
            num_jobs=num_jobs,
            use_exec_script=False,
            active=False,
        )
        self.assertIsNotNone(project)

        project_api = ProjectApi(self.client, project.id)

        job1 = project_api.get_jobs(limit=1)[0]
        job_id = job1.id

        job2 = project_api.get_jobs(id=job_id)[0]
        self.assertEqual(job1, job2)

        job2 = project_api.get_jobs(id=job_id, fields=["id", "name"])[0]
        self.assertNotEqual(job1, job2)

        jms_api = JmsApi(self.client)
        jms_api.delete_project(project)


if __name__ == "__main__":
    unittest.main()
