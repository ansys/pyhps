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

# ----------------------------------------------------------
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging
import unittest

from examples.mapdl_motorbike_frame.project_setup import create_project
from marshmallow.utils import missing

from ansys.hps.client import Client
from ansys.hps.client.jms import JmsApi, ProjectApi
from ansys.hps.client.jms.resource import Job, Project
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class REPClientTest(REPTestCase):
    def test_jms_api(self):

        log.debug("=== Client ===")
        client = self.client
        proj_name = "Mapdl Motorbike Frame"

        log.debug("=== Projects ===")
        jms_api = JmsApi(client)
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

    def test_fields_query_parameter(self):

        client1 = Client(self.rep_url, self.username, self.password, all_fields=False)

        proj_name = "test_fields_query_parameter"
        project = create_project(client1, proj_name, num_jobs=2, use_exec_script=False)

        project_api1 = ProjectApi(client1, project.id)

        jobs = project_api1.get_jobs()
        self.assertEqual(len(jobs), 2)
        self.assertNotEqual(jobs[0].id, missing)
        self.assertNotEqual(jobs[0].eval_status, missing)
        self.assertEqual(jobs[0].values, missing)
        self.assertEqual(jobs[0].host_ids, missing)

        jobs = project_api1.get_jobs(fields=["id", "eval_status", "host_ids"])
        self.assertEqual(len(jobs), 2)
        self.assertNotEqual(jobs[0].id, missing)
        self.assertNotEqual(jobs[0].eval_status, missing)
        self.assertNotEqual(jobs[0].host_ids, missing)
        self.assertEqual(jobs[0].values, missing)

        client2 = Client(self.rep_url, self.username, self.password, all_fields=True)
        project_api2 = ProjectApi(client2, project.id)

        jobs = project_api2.get_jobs()
        self.assertEqual(len(jobs), 2)
        self.assertNotEqual(jobs[0].id, missing)
        self.assertNotEqual(jobs[0].eval_status, missing)
        self.assertNotEqual(jobs[0].values, missing)
        self.assertNotEqual(jobs[0].host_ids, missing)

        jobs = project_api2.get_jobs(fields=["id", "eval_status"])
        self.assertEqual(len(jobs), 2)
        self.assertNotEqual(jobs[0].id, missing)
        self.assertNotEqual(jobs[0].eval_status, missing)
        self.assertEqual(jobs[0].host_ids, missing)
        self.assertEqual(jobs[0].values, missing)

        # Delete project
        JmsApi(client1).delete_project(project)

    def test_storage_configuration(self):

        client = self.client
        jms_api = JmsApi(client)
        storages = jms_api.get_storage()
        for storage in storages:
            self.assertTrue("name" in storage)
            self.assertTrue("priority" in storage)
            self.assertTrue("obj_type" in storage)


if __name__ == "__main__":
    unittest.main()
