# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------
import logging
import unittest

from marshmallow.utils import missing

from ansys.rep.client.jms import JmsApi, ProjectApi
from ansys.rep.client.jms.resource import Algorithm, Job, JobDefinition, Project, Selection
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class AlgorithmsTest(REPTestCase):
    def test_algorithms(self):

        log.debug("=== Client ===")
        client = self.client()
        jms_api = JmsApi(client)
        proj_name = f"rep_client_test_jms_AlgorithmsTest_{self.run_id}"

        proj = Project(name=proj_name, active=True)
        proj = jms_api.create_project(proj, replace=True)
        project_api = ProjectApi(client, proj.id)

        job_def = JobDefinition(name="New Config", active=True)
        job_def = project_api.create_job_definitions([job_def])[0]

        # Create some Jobs
        jobs = [
            Job(name=f"dp_{i}", eval_status="inactive", job_definition_id=job_def.id)
            for i in range(10)
        ]
        jobs = project_api.create_jobs(jobs)

        # Create selections with some jobs
        sels = [Selection(name="selection_0", jobs=[dp.id for dp in jobs[0:5]])]
        sels.append(Selection(name="selection_1", jobs=[dp.id for dp in jobs[5:]]))
        for sel in sels:
            self.assertEqual(len(sel.jobs), 5)
            self.assertEqual(sel.algorithm_id, missing)

        project_api.create_selections(sels)
        sels = project_api.get_selections(fields="all")
        for sel in sels:
            self.assertEqual(len(sel.jobs), 5)
            self.assertEqual(sel.algorithm_id, None)

        # Create an algorithm
        algo = Algorithm(name="new_algo")
        self.assertEqual(algo.data, missing)
        self.assertEqual(algo.description, missing)
        self.assertEqual(algo.jobs, missing)

        algo = project_api.create_algorithms([algo])[0]
        self.assertEqual(len(algo.jobs), 0)
        self.assertEqual(algo.data, None)
        self.assertEqual(algo.description, None)

        # Link jobs to algorithm
        algo.jobs = [j.id for j in jobs]
        algo = project_api.update_algorithms([algo])[0]
        self.assertEqual(len(algo.jobs), 10)

        # Link selections to algorithm
        for sel in sels:
            sel.algorithm_id = algo.id
        sels = project_api.update_selections(sels)

        # Query algorithm selections
        sels = project_api.get_selections(algorithm_id=algo.id)
        for sel in sels:
            self.assertEqual(len(sel.jobs), 5)

        # Query algorithm design points
        jobs = project_api.get_jobs(algorithm_id=algo.id)
        self.assertEqual(len(jobs), 10)

        # Update algorithm
        algo.description = "testing algorithm"
        algo.data = "data"
        algo_id = algo.id
        project_api.update_algorithms([algo])
        algo = project_api.get_algorithms(id=algo_id)[0]
        self.assertEqual(algo.description, "testing algorithm")
        self.assertEqual(algo.data, "data")

        # Delete some design points
        job_ids = [jobs[0].id, jobs[1].id, jobs[6].id, jobs[7].id]
        project_api.delete_jobs([Job(id=f"{j_id}") for j_id in job_ids])
        self.assertEqual(len(project_api.get_jobs()), 6)

        # Delete project
        jms_api.delete_project(proj)


if __name__ == "__main__":
    unittest.main()
