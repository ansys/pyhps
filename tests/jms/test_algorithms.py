# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------
import logging
import sys
import unittest
import urllib.parse
from marshmallow.utils import missing

from ansys.rep.client.jms import Client
from ansys.rep.client.jms.resource import Job, Project, Selection, Algorithm, JobDefinition
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)

class AlgorithmsTest(REPTestCase):
        
    def test_algorithms(self):

        log.debug("=== Client ===")
        client = self.jms_client()
        proj_name = f"rep_client_test_jms_AlgorithmsTest_{self.run_id}"

        proj = Project(name=proj_name, active=True)
        proj = client.create_project(proj, replace=True)

        job_def = JobDefinition(name="New Config", active=True)
        job_def = proj.create_job_definitions([job_def])[0]

        # Create some Jobs        
        jobs = [ Job( name=f"dp_{i}", eval_status="inactive", job_definition_id=job_def.id ) for i in range(10) ]
        jobs = proj.create_jobs(jobs)

        # Create selections with some jobs
        sels = [Selection(name="selection_0", jobs=[dp.id for dp in jobs[0:5]])]
        sels.append( Selection(name="selection_1", jobs=[dp.id for dp in jobs[5:]]) )
        for sel in sels:
            self.assertEqual( len(sel.jobs), 5 )
            self.assertEqual( sel.algorithm_id, missing )

        proj.create_selections(sels)
        sels = proj.get_selections(fields="all")
        for sel in sels:
            self.assertEqual( len(sel.jobs), 5 )
            self.assertEqual( sel.algorithm_id, None )

        # Create an algorithm
        algo = Algorithm(name="new_algo")
        self.assertEqual( algo.data, missing )
        self.assertEqual( algo.description, missing )
        self.assertEqual( algo.jobs, missing )

        algo = proj.create_algorithms([algo])[0]
        self.assertEqual( len(algo.jobs), 0 )
        self.assertEqual( algo.data, None )
        self.assertEqual( algo.description, None )
        
        # Link jobs to algorithm
        algo.jobs = [j.id for j in jobs]
        algo = proj.update_algorithms([algo])[0]
        self.assertEqual( len(algo.jobs), 10 )

        # Link selections to algorithm
        for sel in sels:
            sel.algorithm_id = algo.id
        sels = proj.update_selections(sels)

        # Query algorithm selections
        sels = algo.get_selections()
        for sel in sels:
            self.assertEqual( len(sel.jobs), 5 )

        # Query algorithm design points
        jobs = algo.get_jobs()
        self.assertEqual( len(jobs), 10 )

        # Update algorithm
        algo.description = "testing algorithm"
        algo.data = "data"
        algo_id = algo.id
        proj.update_algorithms([algo])
        algo = proj.get_algorithms(id=algo_id)[0]
        self.assertEqual( algo.description, "testing algorithm" )
        self.assertEqual( algo.data, "data" )

        # Delete some design points
        job_ids = [jobs[0].id, jobs[1].id, jobs[6].id, jobs[7].id]
        proj.delete_jobs([Job(id=f"{j_id}") for j_id in job_ids])
        self.assertEqual(len(proj.get_jobs()), 6)

        # Delete project
        client.delete_project(proj)

if __name__ == '__main__':
    unittest.main()
