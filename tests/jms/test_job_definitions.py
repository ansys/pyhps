import logging

from examples.mapdl_motorbike_frame.project_setup import create_project
from marshmallow.utils import missing

from ansys.hps.client import AuthApi, JmsApi, ProjectApi
from ansys.hps.client.jms.resource import (
    HpcResources,
    JobDefinition,
    Project,
    ResourceRequirements,
    TaskDefinition,
)
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class JobDefinitionsTest(REPTestCase):
    def test_job_definition_delete(self):
        client = self.client
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

        client = self.client
        jms_api = JmsApi(client)
        proj_name = f"test_store_output"

        project = Project(name=proj_name, active=False, priority=10)
        project = jms_api.create_project(project)
        project_api = ProjectApi(client, project.id)
        auth_api = AuthApi(self.client)

        task_def = TaskDefinition(
            name="Task.1",
            execution_command="%executable%",
            max_execution_time=10.0,
            execution_level=0,
            resource_requirements=ResourceRequirements(
                memory=256 * 1024 * 1024 * 1024,  # 256GB
                disk_space=2 * 1024 * 1024 * 1024 * 1024,  # 2TB
                hpc_resources=HpcResources(num_cores_per_node=2),
            ),
        )
        self.assertEqual(task_def.resource_requirements.hpc_resources.num_cores_per_node, 2)

        task_def = project_api.create_task_definitions([task_def])[0]
        self.assertEqual(task_def.store_output, True)
        self.assertEqual(task_def.resource_requirements.memory, 274877906944)
        self.assertEqual(task_def.resource_requirements.disk_space, 2199023255552)
        self.assertEqual(task_def.resource_requirements.hpc_resources.num_cores_per_node, 2)
        self.assertTrue(task_def.modified_by is not missing)
        self.assertTrue(task_def.created_by is not missing)
        self.assertTrue(auth_api.get_user(id=task_def.created_by).username == self.username)
        self.assertTrue(auth_api.get_user(id=task_def.modified_by).username == self.username)

        jms_api.delete_project(project)

    def test_task_and_job_definition_copy(self):

        # create new project
        num_jobs = 1
        project = create_project(
            self.client,
            f"test_task_definition_copy",
            num_jobs=num_jobs,
            use_exec_script=False,
            active=False,
        )
        self.assertIsNotNone(project)

        jms_api = JmsApi(self.client)
        project_api = ProjectApi(self.client, project.id)

        # copy task definition
        task_definitions = project_api.get_task_definitions()
        self.assertEqual(len(task_definitions), 1)

        original_td = task_definitions[0]
        new_td_id = project_api.copy_task_definitions(task_definitions)
        new_td = project_api.get_task_definitions(id=new_td_id)[0]

        self.assertTrue(original_td.name in new_td.name)
        for attr in ["software_requirements", "resource_requirements", "execution_command"]:
            self.assertEqual(getattr(original_td, attr), getattr(new_td, attr))

        # copy job definition
        job_definitions = project_api.get_job_definitions()
        self.assertEqual(len(job_definitions), 1)

        original_jd = job_definitions[0]
        new_jd_id = project_api.copy_job_definitions(job_definitions)
        new_jd = project_api.get_job_definitions(id=new_jd_id)[0]

        self.assertTrue(original_jd.name in new_jd.name)
        self.assertEqual(
            len(original_jd.parameter_definition_ids), len(new_jd.parameter_definition_ids)
        )
        self.assertEqual(len(original_jd.parameter_mapping_ids), len(new_jd.parameter_mapping_ids))
        self.assertEqual(len(original_jd.task_definition_ids), len(new_jd.task_definition_ids))

        jms_api.delete_project(project)
