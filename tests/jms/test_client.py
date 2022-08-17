# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging
import time
import unittest

from ansys.rep.client.jms import Client, ProjectApi, RootApi
from ansys.rep.client.jms.resource import Job, Project
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class REPClientTest(REPTestCase):
    def test_authentication_workflows(self):

        client0 = Client(self.rep_url, self.username, self.password)

        self.assertTrue(client0.access_token is not None)
        self.assertTrue(client0.refresh_token is not None)

        access_token0 = client0.access_token
        refresh_token0 = client0.refresh_token

        # wait a second otherwise the OAuth server will issue the very same tokens
        time.sleep(1)

        client0.refresh_access_token()
        self.assertNotEqual(client0.access_token, access_token0)
        self.assertNotEqual(client0.refresh_token, refresh_token0)

        client1 = Client(self.rep_url, access_token=client0.access_token)
        self.assertEqual(client1.access_token, client0.access_token)
        self.assertTrue(client1.refresh_token is None)

        client2 = Client(self.rep_url, refresh_token=client0.refresh_token)
        self.assertTrue(client2.access_token is not None)
        self.assertNotEqual(client2.refresh_token, client0.refresh_token)
        client2.refresh_access_token()

    def test_client(self):

        # This test assumes that the project mapdl_motorbike_frame already exists on the DCS server.
        # In case, you can create such project running the script
        # examples/mapdl_motorbike_frame/project_setup.py

        log.debug("=== Client ===")
        client = self.jms_client()
        proj_name = "mapdl_motorbike_frame"

        log.debug("=== Projects ===")
        root_api = RootApi(client)
        projects = root_api.get_projects()
        log.debug(f"Projects: {[p.id for p in projects]}")
        project = None
        for p in projects:
            if p.name == proj_name:
                project = p

        if project:
            log.debug(f"Project: {project.id}")
            log.debug(f"project={project}")

        new_proj = Project(name="New project", active=True)
        new_proj = root_api.create_project(new_proj, replace=True)
        # Delete project again
        root_api.delete_project(new_proj)

        log.debug("=== JobDefinitions ===")
        project_api = ProjectApi(client, project.id)
        job_definitions = project_api.get_job_definitions(active=True)
        job_def = job_definitions[0]
        log.debug(f"job_definition={job_def}")

        log.debug("=== Jobs ===")
        all_jobs = project_api.get_jobs(fields="all")
        log.debug(f"# jobs: {len(all_jobs)}")
        if all_jobs:
            log.debug(f"dp0={all_jobs[0]}")

        pending_jobs = project_api.get_jobs(eval_status="pending")
        log.debug(f"Pending jobs: {[j.id for j in pending_jobs]}")

        # Alternative access with manually instantiated project
        proj = root_api.get_projects(name=proj_name)[0]
        project_api = ProjectApi(client, proj.id)
        evaluated_jobs = project_api.get_jobs(eval_status="evaluated", fields="all")
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


if __name__ == "__main__":
    unittest.main()
