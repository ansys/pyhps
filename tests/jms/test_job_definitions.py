import logging

from ansys.rep.client.jms.resource import JobDefinition, Project
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class JobDefinitionsTest(REPTestCase):
    def test_job_definition_delete(self):
        client = self.jms_client()
        proj_name = f"rep_client_test_jms_JobDefinitionTest_{self.run_id}"

        proj = Project(name=proj_name, active=True)
        proj = client.create_project(proj, replace=True)

        job_def = JobDefinition(name="New Config", active=True)
        job_def = proj.create_job_definitions([job_def])[0]

        assert len(proj.get_job_definitions()) == 1

        proj.delete_job_definitions([JobDefinition(id=job_def.id)])

        assert len(proj.get_job_definitions()) == 0

        client.delete_project(proj)
