# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging
import unittest

from ansys.rep.client.jms import JmsApi, ProjectApi
from ansys.rep.client.jms.resource import Job, Project
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class REPClientTest(REPTestCase):
    def test_jms_api(self):

        # This test assumes that the project mapdl_motorbike_frame already exists on the DCS server.
        # In case, you can create such project running the script
        # examples/mapdl_motorbike_frame/project_setup.py

        log.debug("=== Client ===")
        client = self.client()
        proj_name = "mapdl_motorbike_frame"

        log.debug("=== Projects ===")
        jms_api = JmsApi(client)
        projects = jms_api.get_projects()
        log.debug(f"Projects: {[p.id for p in projects]}")
        project = None
        for p in projects:
            if p.name == proj_name:
                project = p

        if project:
            log.debug(f"Project: {project.id}")
            log.debug(f"project={project}")

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
        all_jobs = project_api.get_jobs(fields="all")
        log.debug(f"# jobs: {len(all_jobs)}")
        if all_jobs:
            log.debug(f"dp0={all_jobs[0]}")

        pending_jobs = project_api.get_jobs(eval_status="pending")
        log.debug(f"Pending jobs: {[j.id for j in pending_jobs]}")

        # Alternative access with manually instantiated project
        proj = jms_api.get_projects(name=proj_name)[0]
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
