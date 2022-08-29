# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------
import logging
import os
import tempfile
import time
import unittest

from examples.mapdl_motorbike_frame.project_setup import create_project as motorbike_create_project
from marshmallow.utils import missing

from ansys.rep.client.jms import JmsApi, ProjectApi
from ansys.rep.client.jms.resource import JobDefinition, LicenseContext, Project
from ansys.rep.client.jms.schema.project import ProjectSchema
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class ProjectsTest(REPTestCase):
    def test_project_deserialization(self):

        project_dict = {
            "name": "Fluent_2D_Cooling_mp",
            "active": False,
            "priority": 0,
            # "creation_time": "2019-05-28T11:37:23.361446+02:00",
            "statistics": {
                "eval_status": {
                    "inactive": 1,
                    "failed": 2,
                    "timeout": 0,
                    "aborted": 3,
                    "pending": 0,
                    "prolog": 8,
                    "running": 9,
                    "evaluated": 33,
                },
                "num_jobs": 56,
            },
            "file_storages": [
                {
                    "obj_type": "RestGateway",
                    "name": "dc_fs_gateway",
                    "url": "https://212.126.163.153:443/dcs/fs/api",
                    "use_default_url": False,
                    "priority": 20,
                    "reference": "file_system_storage",
                },
                {
                    "obj_type": "FileSystemStorage",
                    "name": "file_system_storage",
                    "cache": False,
                    "persistent": True,
                    "priority": 10,
                    "storage_directory": "/media/dcp_data/ansft_gateway/default_fs_storage/",
                    "owner_uuid": "0ea21dc4-37da-46e2-85e2-4f4a78dcdf0a",
                },
                {
                    "obj_type": "FileSystemStorage",
                    "name": "shared_file_system_storage",
                    "cache": False,
                    "persistent": True,
                    "priority": 5,
                    "storage_directory": "/media/ansys/tmp_storage/",
                    "owner_uuid": "0ea21dc4-37da-46e2-85e2-4f4a78dcdf0a",
                },
            ],
        }

        project = ProjectSchema().load(project_dict)

        self.assertEqual(project.__class__.__name__, "Project")
        self.assertEqual(project.creation_time, missing)
        self.assertEqual(project.name, project_dict["name"])

        self.assertEqual(
            project.statistics["eval_status"]["prolog"],
            project_dict["statistics"]["eval_status"]["prolog"],
        )
        self.assertEqual(
            project.statistics["eval_status"]["failed"],
            project_dict["statistics"]["eval_status"]["failed"],
        )

        self.assertEqual(len(project.file_storages), 3)
        self.assertEqual(project.file_storages[0]["name"], "dc_fs_gateway")
        self.assertEqual(project.file_storages[0]["reference"], "file_system_storage")
        self.assertEqual(project.file_storages[2]["storage_directory"], "/media/ansys/tmp_storage/")

    def test_project_serialization(self):

        project = Project(name="new_project", replace=False)

        self.assertEqual(project.creation_time, missing)
        self.assertEqual(project.statistics, missing)

        serialized_project = ProjectSchema().dump(project)

        self.assertTrue("name" in serialized_project.keys())
        self.assertFalse("file_storages" in serialized_project.keys())
        self.assertEqual(serialized_project["name"], "new_project")

    def test_project_integration(self):

        client = self.client()
        jms_api = JmsApi(client)
        proj_name = f"test_jms_ProjectTest_{self.run_id}"

        proj = Project(name=proj_name, active=True, priority=10)
        proj = jms_api.create_project(proj, replace=True)

        proj = jms_api.get_project(id=proj.id)
        self.assertTrue(proj.creation_time is not None)
        self.assertEqual(proj.priority, 10)
        self.assertEqual(proj.active, True)

        proj = jms_api.get_projects(name=proj.name, statistics=True)[0]
        self.assertEqual(proj.statistics["num_jobs"], 0)

        # statistics["eval_status"] might get few seconds until is populated on the server
        timeout = time.time() + 120
        while not proj.statistics["eval_status"] and time.time() < timeout:
            time.sleep(5)
            proj = jms_api.get_projects(id=proj.id, statistics=True)[0]
        self.assertEqual(proj.statistics["eval_status"]["prolog"], 0)
        self.assertEqual(proj.statistics["eval_status"]["failed"], 0)

        proj = jms_api.get_project(id=proj.id)
        proj.active = False
        proj = jms_api.update_project(proj)
        self.assertEqual(proj.active, False)

        # Delete project
        jms_api.delete_project(proj)

    def test_project_replace(self):

        client = self.client()
        jms_api = JmsApi(client)

        p = Project(name="Original Project")
        p = jms_api.create_project(p)
        project_id = p.id
        p.name = "Replaced Project"
        p = jms_api.create_project(p, replace=True)

        self.assertEqual(p.id, project_id)
        self.assertEqual(p.name, "Replaced Project")

    def test_project_copy(self):

        client = self.client()
        jms_api = JmsApi(client)
        proj_name = f"test_jms_ProjectCopyTest_{self.run_id}"

        proj = Project(name=proj_name, active=True, priority=10)
        proj = jms_api.create_project(proj, replace=True)

        tgt_name = proj_name + "_copy1"
        project_api = ProjectApi(client, proj.id)
        proj1_id = project_api.copy_project(tgt_name)
        copied_proj1 = jms_api.get_project(name=tgt_name)
        self.assertIsNotNone(copied_proj1)

        tgt_name = proj_name + "_copy2"
        project_api.copy_project(tgt_name)
        copied_proj2 = jms_api.get_project(name=tgt_name)
        self.assertIsNotNone(copied_proj2)

        # Delete projects
        jms_api.delete_project(copied_proj1)
        jms_api.delete_project(copied_proj2)
        jms_api.delete_project(proj)

    @unittest.expectedFailure
    def test_project_license_context(self):

        client = self.client()
        jms_api = JmsApi(client)
        proj_name = f"test_jms_ProjectTest_license_context_{self.run_id}"

        proj = Project(id=proj_name, active=True, priority=10)
        proj = jms_api.create_project(proj, replace=True)
        project_api = ProjectApi(client, proj.id)

        # Create new license context in JMS
        license_contexts = project_api.create_license_contexts()
        self.assertEqual(len(license_contexts), 1)
        self.assertGreater(len(license_contexts[0].context_id), 0)
        self.assertEqual(len(license_contexts[0].environment), 2)

        license_contexts = project_api.get_license_contexts()
        self.assertEqual(len(license_contexts), 1)
        self.assertGreater(len(license_contexts[0].context_id), 0)
        self.assertEqual(len(license_contexts[0].environment), 2)

        # Terminate license context
        project_api.delete_license_contexts()
        license_contexts = project_api.get_license_contexts()
        self.assertEqual(len(license_contexts), 0)

        # Set a license context from outside=
        lc = LicenseContext(
            environment={
                "ANSYS_HPC_PARAMETRIC_ID": "my_id",
                "ANSYS_HPC_PARAMETRIC_SERVER": "my_server",
            }
        )
        license_contexts = project_api.update_license_contexts([lc])
        self.assertEqual(len(license_contexts), 1)
        self.assertEqual(license_contexts[0].context_id, "my_id")
        self.assertEqual(len(license_contexts[0].environment), 2)
        self.assertEqual(license_contexts[0].environment["ANSYS_HPC_PARAMETRIC_ID"], "my_id")
        self.assertEqual(
            license_contexts[0].environment["ANSYS_HPC_PARAMETRIC_SERVER"], "my_server"
        )

        license_contexts = project_api.get_license_contexts()
        self.assertEqual(len(license_contexts), 1)
        self.assertEqual(license_contexts[0].context_id, "my_id")
        self.assertEqual(len(license_contexts[0].environment), 2)
        self.assertEqual(license_contexts[0].environment["ANSYS_HPC_PARAMETRIC_ID"], "my_id")
        self.assertEqual(
            license_contexts[0].environment["ANSYS_HPC_PARAMETRIC_SERVER"], "my_server"
        )

        # Remove the license context set from outside again
        project_api.delete_license_contexts()
        license_contexts = project_api.get_license_contexts()
        self.assertEqual(len(license_contexts), 0)

        # Delete project
        jms_api.delete_project(proj)

    def test_project_delete_job_definition(self):

        client = self.client()
        jms_api = JmsApi(client)
        proj_name = f"test_jms_ProjectTest_delete_config_{self.run_id}"

        proj = Project(name=proj_name, active=True, priority=10)
        proj = jms_api.create_project(proj, replace=True)

        project_api = ProjectApi(client, proj.id)

        job_def = JobDefinition(name="Config1")
        job_def = project_api.create_job_definitions([job_def])[0]
        self.assertEqual(len(project_api.get_job_definitions()), 1)
        project_api.delete_job_definitions([job_def])
        self.assertEqual(len(project_api.get_job_definitions()), 0)

        jms_api.delete_project(proj)

    def test_project_archive_restore(self):

        num_jobs = 2
        client = self.client()
        jms_api = JmsApi(client)
        proj_name = f"test_jms_project_archive_restore_{self.run_id}"

        # Setup project to work with
        project = motorbike_create_project(client=client, name=proj_name, num_jobs=num_jobs)
        project.active = False
        project.priority = 6
        project = jms_api.update_project(project)

        restored_project = None
        project_api = ProjectApi(client, project.id)
        with tempfile.TemporaryDirectory() as tpath:

            # Archive project
            archive_path = project_api.archive_project(tpath, include_job_files=True)
            self.assertTrue(os.path.exists(archive_path))
            log.info(f"Archive size {os.path.getsize(archive_path)} bytes")
            self.assertGreater(os.path.getsize(archive_path), 2e3)  # file larger than 2 KB size

            # Restore project
            restored_project = jms_api.restore_project(archive_path)
            restored_project_api = ProjectApi(client, restored_project.id)

            self.assertEqual(restored_project.active, False)
            self.assertEqual(restored_project.priority, 6)
            self.assertEqual(
                len(project_api.get_job_definitions()),
                len(restored_project_api.get_job_definitions()),
            )
            self.assertEqual(len(project_api.get_jobs()), len(restored_project_api.get_jobs()))

        jms_api.delete_project(project)
        jms_api.delete_project(restored_project)


if __name__ == "__main__":
    unittest.main()