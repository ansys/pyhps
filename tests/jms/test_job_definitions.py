import logging

from ansys.rep.client.jms import JmsApi, ProjectApi
from ansys.rep.client.jms.resource import JobDefinition, Project
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class JobDefinitionsTest(REPTestCase):
    def test_job_definition_delete(self):
        client = self.client()
        proj_name = f"rep_client_test_jms_JobDefinitionTest_{self.run_id}"

        proj = Project(name=proj_name, active=True)
        jms_api = JmsApi(client)
        proj = jms_api.create_project(proj, replace=True)
        project_api = ProjectApi(client, proj.id)

        job_def = JobDefinition(name="New Config", active=True)
        job_def = project_api.create_job_definitions([job_def])[0]

        assert len(project_api.get_job_definitions()) == 1

        project_api.delete_job_definitions([JobDefinition(id=job_def.id)])

        assert len(project_api.get_job_definitions()) == 0

        jms_api.delete_project(proj)
