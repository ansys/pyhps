# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging
import sys
import time
import unittest
import urllib.parse
from marshmallow.utils import missing

from ansys.rep.client.jms import Client
from ansys.rep.client.jms.resource import Job, Project, JobDefinition
from test.rep_test import REPTestCase

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
        # In case, you can create such project running the script examples/mapdl_motorbike_frame/project_setup.py   

        log.debug("=== Client ===")
        client = self.jms_client()
        proj_name="mapdl_motorbike_frame"

        log.debug("=== Projects ===")
        projects=client.get_projects()
        log.debug(f"Projects: {[p.id for p in projects]}")
        project = None
        for p in projects:
            if p.name == proj_name:
                project = p

        if project:
            log.debug(f"Project: {project.id}")
            log.debug(f"project={project}")

        new_proj=Project(name="New project", active=True)
        new_proj=client.create_project(new_proj, replace=True)
        # Delete project again
        client.delete_project(new_proj)

        log.debug("=== JobDefinitions ===")
        job_definitions=project.get_job_definitions(active=True)
        job_def=job_definitions[0]
        log.debug(f"job_definition={job_def}")

        log.debug("=== Design Points ===")
        all_jobs = project.get_jobs(fields="all")
        log.debug(f"# design points: {len(all_jobs)}")
        if all_jobs:
            log.debug(f"dp0={all_jobs[0]}")

        pending_jobs = project.get_jobs(eval_status="pending")
        log.debug(f"Pending design points: {[j.id for j in pending_jobs]}")

        # Alternative access with manually instantiated project
        proj = client.get_projects(name=proj_name)[0]
        evaluated_jobs=proj.get_jobs(eval_status="evaluated", fields="all")
        log.debug(f"Evaluated design points: {[j.id for j in evaluated_jobs]}")

        # Access design point data without objects
        dp_data = project.get_jobs(limit=3, as_objects=False)
        log.debug(f"dp_data={dp_data}")
            
        # Create some Jobs        
        new_jobs=[ Job( name=f"new_dp_{i}", eval_status="pending" ) for i in range(10) ]
        created_jobs=job_def.create_jobs(new_jobs)

        # Delete Jobs again
        job_def.delete_jobs(created_jobs)

        
if __name__ == '__main__':
    unittest.main()
