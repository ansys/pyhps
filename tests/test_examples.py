import logging
import unittest

from ansys.rep.client import __ansys_apps_version__ as ansys_version
from ansys.rep.client.jms import JmsApi, ProjectApi
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class REPClientTest(REPTestCase):
    def test_mapdl_motorbike_frame(self):

        from examples.mapdl_motorbike_frame.project_setup import create_project

        num_jobs = 5
        project = create_project(
            self.client, f"Test mapdl_motorbike_frame", num_jobs=num_jobs, use_exec_script=False
        )
        self.assertIsNotNone(project)

        jms_api = JmsApi(self.client)
        project_api = ProjectApi(self.client, project.id)

        self.assertEqual(len(project_api.get_jobs()), num_jobs)
        td = project_api.get_task_definitions()[0]
        self.assertEqual(len(td.success_criteria.required_output_file_ids), 1)

        jms_api.delete_project(project)

    def test_mapdl_motorbike_frame_with_exec_script(self):

        from examples.mapdl_motorbike_frame.project_setup import create_project

        num_jobs = 5
        project = create_project(
            self.client, f"Test mapdl_motorbike_frame", num_jobs=num_jobs, use_exec_script=True
        )
        self.assertIsNotNone(project)

        jms_api = JmsApi(self.client)
        project_api = ProjectApi(self.client, project.id)

        self.assertEqual(len(project_api.get_jobs()), num_jobs)

        jms_api.delete_project(project)

    def test_mapdl_motorbike_frame_with_user_defined_version(self):

        from examples.mapdl_motorbike_frame.project_setup import create_project

        num_jobs = 5
        project = create_project(
            self.client,
            f"Test mapdl_motorbike_frame",
            version="2022 R1",
            num_jobs=num_jobs,
            use_exec_script=False,
        )
        self.assertIsNotNone(project)

        jms_api = JmsApi(self.client)
        project_api = ProjectApi(self.client, project.id)

        self.assertEqual(len(project_api.get_jobs()), num_jobs)

        job_def = project_api.get_job_definitions()[0]
        task_def = project_api.get_task_definitions(id=job_def.task_definition_ids)[0]
        app = task_def.software_requirements[0]
        self.assertEqual(app.name, "Ansys Mechanical APDL")
        self.assertEqual(app.version, "2022 R1")

        jms_api.delete_project(project)

    def test_mapdl_tyre_performance(self):

        from examples.mapdl_tyre_performance.project_setup import main

        num_jobs = 1
        project = main(self.client, f"Test mapdl_tyre_performance", num_jobs, version=ansys_version)
        self.assertIsNotNone(project)

        jms_api = JmsApi(self.client)
        project_api = ProjectApi(self.client, project.id)

        self.assertEqual(len(project_api.get_jobs()), num_jobs)

        jms_api.delete_project(project)

    def test_python_two_bar_truss_problem(self):

        from examples.python_two_bar_truss_problem.project_setup import main

        num_jobs = 10
        project = main(self.client, num_jobs, use_exec_script=False)
        self.assertIsNotNone(project)

        jms_api = JmsApi(self.client)
        project_api = ProjectApi(self.client, project.id)

        self.assertEqual(len(project_api.get_jobs()), num_jobs)

        jms_api.delete_project(project)

    def test_python_two_bar_truss_problem_with_exec_script(self):

        from examples.python_two_bar_truss_problem.project_setup import main

        num_jobs = 10
        project = main(self.client, num_jobs, use_exec_script=True)
        self.assertIsNotNone(project)

        jms_api = JmsApi(self.client)
        project_api = ProjectApi(self.client, project.id)

        self.assertEqual(len(project_api.get_jobs()), num_jobs)

        jms_api.delete_project(project)

    def test_mapdl_linked_analyses(self):

        from examples.mapdl_linked_analyses.project_setup import create_project

        client = self.client

        for incremental_version in [True, False]:
            project = create_project(
                client,
                name="Test Linked Analyses",
                incremental=incremental_version,
                version=ansys_version,
            )
            self.assertIsNotNone(project)

            jms_api = JmsApi(client)
            project_api = ProjectApi(client, project.id)

            self.assertEqual(len(project_api.get_jobs()), 1)
            self.assertEqual(len(project_api.get_tasks()), 3)

            jms_api.delete_project(project)

    def test_fluent_2d_heat_exchanger(self):

        from examples.fluent_2d_heat_exchanger.project_setup import main

        project = main(self.client, name="Fluent Test", version=ansys_version)
        self.assertIsNotNone(project)

        jms_api = JmsApi(self.client)
        project_api = ProjectApi(self.client, project.id)

        self.assertEqual(len(project_api.get_jobs()), 1)
        self.assertEqual(jms_api.get_project(id=project.id).name, "Fluent Test")

        jms_api.delete_project(project)

    def test_fluent_nozzle(self):

        from examples.fluent_nozzle.project_setup import create_project

        project = create_project(
            self.client, name="Fluent Nozzle Test", num_jobs=1, version=ansys_version
        )
        self.assertIsNotNone(project)

        jms_api = JmsApi(self.client)
        project_api = ProjectApi(self.client, project.id)

        self.assertEqual(len(project_api.get_jobs()), 1)
        self.assertEqual(jms_api.get_project(id=project.id).name, "Fluent Nozzle Test")

        jms_api.delete_project(project)

    def test_cfx_static_mixer(self):

        from examples.cfx_static_mixer.project_setup import create_project

        project = create_project(
            self.client, name="CFX Static Mixer Test", num_jobs=1, version=ansys_version
        )
        self.assertIsNotNone(project)

        jms_api = JmsApi(self.client)
        project_api = ProjectApi(self.client, project.id)

        self.assertEqual(len(project_api.get_jobs()), 1)
        self.assertEqual(jms_api.get_project(id=project.id).name, "CFX Static Mixer Test")

        jms_api.delete_project(project)


if __name__ == "__main__":
    unittest.main()
