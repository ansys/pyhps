# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------
import logging
import time
import unittest
import os
import tempfile
from marshmallow.utils import missing

from ansys.rep.client.jms import Client
from ansys.rep.client.jms.resource import Project, LicenseContext, JobDefinition
from ansys.rep.client.jms.schema.project import ProjectSchema
from tests.rep_test import REPTestCase
from examples.mapdl_motorbike_frame.project_setup import create_project

log = logging.getLogger(__name__)


class ProjectsTest(REPTestCase):
        
    def test_project_deserialization(self):

        project_dict = {
            "name": "Fluent_2D_Cooling_mp",
            "active": False,
            "priority": 0,
            #"creation_time": "2019-05-28T11:37:23.361446+02:00",
            "statistics": {
                "eval_status": {
                    "inactive": 1,
                    "failed": 2,
                    "timeout": 0,
                    "aborted": 3,
                    "pending": 0,
                    "prolog": 8,
                    "running": 9,
                    "evaluated": 33
                },
                "num_jobs": 56
            },
            "file_storages": [
                  {
                      "obj_type": "RestGateway",
                      "name": "dc_fs_gateway",
                      "url": "https://212.126.163.153:443/dcs/fs/api",
                      "use_default_url": False,
                      "priority": 20,
                      "reference": "file_system_storage"
                  },
                  {
                      "obj_type": "FileSystemStorage",
                      "name": "file_system_storage",
                      "cache": False,
                      "persistent": True,
                      "priority": 10,
                      "storage_directory": "/media/dcp_data/ansft_gateway/default_fs_storage/",
                      "owner_uuid": "0ea21dc4-37da-46e2-85e2-4f4a78dcdf0a"
                  },
                  {
                      "obj_type": "FileSystemStorage",
                      "name": "shared_file_system_storage",
                      "cache": False,
                      "persistent": True,
                      "priority": 5,
                      "storage_directory": "/media/ansys/tmp_storage/",
                      "owner_uuid": "0ea21dc4-37da-46e2-85e2-4f4a78dcdf0a"
                  }
            ],
        }

        project = ProjectSchema().load( project_dict )
        
        self.assertEqual(project.__class__.__name__, "Project")
        self.assertEqual(project.creation_time, missing)
        self.assertEqual(project.name, project_dict["name"])

        self.assertEqual(project.statistics["eval_status"]["prolog"], project_dict["statistics"]["eval_status"]["prolog"])
        self.assertEqual(project.statistics["eval_status"]["failed"], project_dict["statistics"]["eval_status"]["failed"])
        
        self.assertEqual(len(project.file_storages), 3)
        self.assertEqual(project.file_storages[0]["name"], "dc_fs_gateway")
        self.assertEqual(project.file_storages[0]["reference"], "file_system_storage")
        self.assertEqual(project.file_storages[2]["storage_directory"], "/media/ansys/tmp_storage/")

    def test_project_serialization(self):

        project = Project(name="new_project", replace=False)

        self.assertEqual(project.creation_time, missing)
        self.assertEqual(project.statistics, missing )

        serialized_project = ProjectSchema().dump(project)

        self.assertTrue( "name" in serialized_project.keys() )
        self.assertFalse( "file_storages" in serialized_project.keys() )
        self.assertEqual( serialized_project["name"], "new_project" )


    def test_project_integration(self):

        client = self.jms_client()
        proj_name = f"test_dps_ProjectTest_{self.run_id}"

        proj = Project(name=proj_name, active=True, priority=10)
        proj = client.create_project(proj, replace=True)

        proj = client.get_project(id=proj.id)
        self.assertTrue( proj.creation_time is not None )
        self.assertEqual( proj.priority, 10 )
        self.assertEqual( proj.active, True )

        proj = client.get_projects(name=proj.name, statistics=True)[0]
        self.assertEqual( proj.statistics["num_jobs"], 0 )

        # statistics["eval_status"] might get few seconds until is populated on the server
        timeout = time.time() + 120
        while not proj.statistics["eval_status"] and time.time() < timeout:
            time.sleep(5)
            proj = client.get_projects(id=proj.id, statistics=True)[0]
        self.assertEqual( proj.statistics["eval_status"]["prolog"], 0 )
        self.assertEqual( proj.statistics["eval_status"]["failed"], 0 )

        proj = client.get_project(id=proj.id)
        proj.active = False
        proj = client.update_project(proj)
        self.assertEqual( proj.active, False )

        # Delete project
        client.delete_project(proj)

    def test_project_copy(self):

        client = self.jms_client()
        proj_name = f"test_dps_ProjectCopyTest_{self.run_id}"

        proj = Project(name=proj_name, active=True, priority=10)
        proj = client.create_project(proj, replace=True)

        tgt_name = proj_name + "_copy1"
        proj1_id = client.copy_project(proj, tgt_name)
        copied_proj1 = client.get_project(name=tgt_name)
        self.assertIsNotNone(copied_proj1)

        tgt_name = proj_name + "_copy2"
        proj.copy(tgt_name)
        copied_proj2 = client.get_project(name=tgt_name)
        self.assertIsNotNone(copied_proj2)
        
        # Delete projects
        client.delete_project(copied_proj1)
        client.delete_project(copied_proj2)
        client.delete_project(proj)

    @unittest.expectedFailure
    def test_project_license_context(self):

        client = self.jms_client()
        proj_name = f"test_dps_ProjectTest_license_context_{self.run_id}"

        proj = Project(id=proj_name, active=True, priority=10)
        proj = client.create_project(proj, replace=True)

        # Create new license context in DPS
        license_contexts = proj.create_license_contexts()
        self.assertEqual(len(license_contexts), 1)
        self.assertGreater(len(license_contexts[0].context_id), 0)
        self.assertEqual(len(license_contexts[0].environment), 2)

        license_contexts = proj.get_license_contexts()
        self.assertEqual(len(license_contexts), 1)
        self.assertGreater(len(license_contexts[0].context_id), 0)
        self.assertEqual(len(license_contexts[0].environment), 2)

        # Terminate license context
        proj.delete_license_contexts()
        license_contexts = proj.get_license_contexts()
        self.assertEqual(len(license_contexts), 0)

        # Set a license context from outside=
        lc= LicenseContext(environment={"ANSYS_HPC_PARAMETRIC_ID": "my_id", "ANSYS_HPC_PARAMETRIC_SERVER":"my_server" })
        license_contexts = proj.update_license_contexts([lc])
        self.assertEqual(len(license_contexts), 1)
        self.assertEqual(license_contexts[0].context_id, "my_id")
        self.assertEqual(len(license_contexts[0].environment), 2)
        self.assertEqual(license_contexts[0].environment["ANSYS_HPC_PARAMETRIC_ID"], "my_id")
        self.assertEqual(license_contexts[0].environment["ANSYS_HPC_PARAMETRIC_SERVER"], "my_server")

        license_contexts = proj.get_license_contexts()
        self.assertEqual(len(license_contexts), 1)
        self.assertEqual(license_contexts[0].context_id, "my_id")
        self.assertEqual(len(license_contexts[0].environment), 2)
        self.assertEqual(license_contexts[0].environment["ANSYS_HPC_PARAMETRIC_ID"], "my_id")
        self.assertEqual(license_contexts[0].environment["ANSYS_HPC_PARAMETRIC_SERVER"], "my_server")
         
        # Remove the license context set from outside again
        proj.delete_license_contexts()
        license_contexts = proj.get_license_contexts()
        self.assertEqual(len(license_contexts), 0)

        # Delete project
        client.delete_project(proj)

    def test_project_delete_job_definition(self):

        client = self.jms_client()
        proj_name = f"test_dps_ProjectTest_delete_config_{self.run_id}"

        proj = Project(name=proj_name, active=True, priority=10)
        proj = client.create_project(proj, replace=True)

        job_def = JobDefinition(name="Config1")
        job_def = proj.create_job_definitions([job_def])[0]
        self.assertEqual(len(proj.get_job_definitions()), 1)
        proj.delete_job_definitions([job_def])
        self.assertEqual(len(proj.get_job_definitions()), 0)

        client.delete_project(proj)

    def test_project_archive_restore(self):

        num_jobs = 2
        client = self.jms_client()
        proj_name = f"test_dps_project_archive_restore_{self.run_id}"

        # Setup project to work with
        project = create_project(
            client=client, name=proj_name, num_jobs=num_jobs)
        project.active = False
        project.priority = 6
        project = client.update_project(project)

        restored_proj_name = f"{proj_name}-restored"
        restored_project = None
        with tempfile.TemporaryDirectory() as tpath:
            
            # Archive project
            archive_path = client.archive_project(project, tpath, include_job_files=True)
            self.assertTrue(os.path.exists(archive_path))
            log.info(f"Archive size {os.path.getsize(archive_path)} bytes")
            self.assertGreater(os.path.getsize(archive_path), 2e+3) # file larger than 2 KB size
            
            # Restore project
            restored_project = client.restore_project(archive_path, restored_proj_name)

            self.assertEqual(restored_project.active, False)
            self.assertEqual(restored_project.priority, 6)
            self.assertEqual(len(project.get_job_definitions()), len(restored_project.get_job_definitions())) 
            self.assertEqual(len(project.get_jobs()), len(restored_project.get_jobs())) 

        client.delete_project(project)
        client.delete_project(restored_project)
        
if __name__ == '__main__':
    unittest.main()
