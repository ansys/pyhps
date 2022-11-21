import logging

from ansys.rep.client.jms import JmsApi, ProjectApi
from ansys.rep.client.jms.resource import (
    JobDefinition,
    Project,
    ResourceRequirements,
    TaskDefinition,
)
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

    def test_task_definition_fields(self):

        # verify that:
        # - store_output is defaulted to True when undefined,
        # - memory and disk_space are correctly stored in bytes

        client = self.client()
        jms_api = JmsApi(client)
        proj_name = f"test_store_output"

        project = Project(name=proj_name, active=False, priority=10)
        project = jms_api.create_project(project)
        project_api = ProjectApi(client, project.id)

        task_def = TaskDefinition(
            name="Task.1",
            application_name="MyApp",
            application_version="1.0.0",
            execution_command="%executable%",
            max_execution_time=10.0,
            execution_level=0,
            resource_requirements=ResourceRequirements(
                memory=256 * 1024 * 1024 * 1024,  # 256GB
                disk_space=2 * 1024 * 1024 * 1024 * 1024,  # 2TB
            ),
        )
        task_def = project_api.create_task_definitions([task_def])[0]
        self.assertEqual(task_def.store_output, True)
        self.assertEqual(task_def.resource_requirements.memory, 274877906944)
        self.assertEqual(task_def.resource_requirements.disk_space, 2199023255552)

        jms_api.delete_project(project)
