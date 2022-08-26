import logging
import unittest

from ansys.rep.client.jms import JmsApi, ProjectApi
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class REPClientTest(REPTestCase):
    def test_mapdl_motorbike_frame(self):

        from examples.mapdl_motorbike_frame.project_setup import create_project

        num_jobs = 5
        project = create_project(
            self.client(), f"Test mapdl_motorbike_frame", num_jobs=num_jobs, use_exec_script=False
        )
        self.assertIsNotNone(project)

        jms_api = JmsApi(self.client())
        project_api = ProjectApi(self.client(), project.id)

        self.assertEqual(len(project_api.get_jobs()), num_jobs)

        jms_api.delete_project(project)

    def test_mapdl_motorbike_frame_with_exec_script(self):

        from examples.mapdl_motorbike_frame.project_setup import create_project

        num_jobs = 5
        project = create_project(
            self.client(), f"Test mapdl_motorbike_frame", num_jobs=num_jobs, use_exec_script=True
        )
        self.assertIsNotNone(project)

        jms_api = JmsApi(self.client())
        project_api = ProjectApi(self.client(), project.id)

        self.assertEqual(len(project_api.get_jobs()), num_jobs)

        jms_api.delete_project(project)

    def test_mapdl_tyre_performance(self):

        from examples.mapdl_tyre_performance.project_setup import main

        num_jobs = 1
        project = main(self.client(), f"Test mapdl_tyre_performance", num_jobs)
        self.assertIsNotNone(project)

        jms_api = JmsApi(self.client())
        project_api = ProjectApi(self.client(), project.id)

        self.assertEqual(len(project_api.get_jobs()), num_jobs)

        jms_api.delete_project(project)

    def test_python_two_bar_truss_problem(self):

        from examples.python_two_bar_truss_problem.project_setup import main

        num_jobs = 10
        project = main(self.client(), num_jobs, use_exec_script=False)
        self.assertIsNotNone(project)

        jms_api = JmsApi(self.client())
        project_api = ProjectApi(self.client(), project.id)

        self.assertEqual(len(project_api.get_jobs()), num_jobs)

        jms_api.delete_project(project)

    def test_python_two_bar_truss_problem_with_exec_script(self):

        from examples.python_two_bar_truss_problem.project_setup import main

        num_jobs = 10
        project = main(self.client(), num_jobs, use_exec_script=True)
        self.assertIsNotNone(project)

        jms_api = JmsApi(self.client())
        project_api = ProjectApi(self.client(), project.id)

        self.assertEqual(len(project_api.get_jobs()), num_jobs)

        jms_api.delete_project(project)

    def test_mapdl_linked_analyses(self):

        from examples.mapdl_linked_analyses.project_setup import create_project

        client = self.client()

        for incremental_version in [True, False]:
            project = create_project(
                client, name="Test Linked Analyses", incremental=incremental_version
            )
            self.assertIsNotNone(project)

            jms_api = JmsApi(client)
            project_api = ProjectApi(client, project.id)

            self.assertEqual(len(project_api.get_jobs()), 1)
            self.assertEqual(len(project_api.get_tasks()), 3)

            jms_api.delete_project(project)


if __name__ == "__main__":
    unittest.main()
