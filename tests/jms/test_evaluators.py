# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------

import json
import logging
import unittest

from marshmallow.utils import missing

from ansys.rep.client.jms.schema.evaluator import EvaluatorSchema
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class EvaluatorTest(REPTestCase):
    def test_evaluator_deserialization(self):

        evaluator_dict = {
            "project_server_select": True,
            # "alive_update_interval": 15,
            "id": "02q1DiPEP0nanLN5384q8L",
            "update_time": "2019-05-07T05:42:52.493419+00:00",
            "project_assignment_mode": "all_active",
            # "platform": "Windows",
            "task_manager_type": "Direct",
            "hostname": "dc_evaluator_win10_2019R3_tmp",
            "host_id": "db337a96-ebbb-362a-8c02-1103c15e2b43",
            "name": "dc_evaluator_win10_2019R3_tmp",
            "project_list": [],
            "external_access_port": 443,
        }

        evaluator = EvaluatorSchema().load(evaluator_dict)

        self.assertEqual(evaluator.__class__.__name__, "Evaluator")
        self.assertEqual(evaluator.platform, missing)
        self.assertEqual(evaluator.alive_update_interval, missing)
        self.assertEqual(evaluator.name, evaluator_dict["name"])
        self.assertEqual(len(evaluator.project_list), 0)

        evaluator_dict["project_assignment_mode"] = "project_list"
        evaluator_dict["project_list"] = ["proj1", "proj2"]

        evaluator = EvaluatorSchema().load(evaluator_dict)
        self.assertEqual(evaluator.project_assignment_mode, "project_list")
        self.assertEqual(len(evaluator.project_list), 2)
        self.assertEqual(evaluator.project_list[1], "proj2")

    def test_evaluator_integration(self):

        client = self.jms_client()
        evaluators = client.get_evaluators()

        if evaluators:
            self.assertTrue(evaluators[0].id is not None)

        evaluators = client.get_evaluators(as_objects=False)
        if evaluators:
            self.assertTrue(evaluators[0]["id"] is not None)

        evaluators = client.get_evaluators(as_objects=False, fields=["hostname", "platform"])
        log.info(f"evaluators={evaluators}")
        if evaluators:
            self.assertTrue("hostname" in evaluators[0].keys())
            self.assertTrue("platform" in evaluators[0].keys())
            self.assertTrue("project_server_select" not in evaluators[0].keys())
            # self.assertEqual(len(evaluators[0].keys()), 2)

        evaluators = client.get_evaluators(fields=["hostname", "platform", "configuration"])

        if evaluators:
            i = next(i for i, e in enumerate(evaluators) if e.configuration)
            log.info(f"Index: {i}")

            self.assertFalse(evaluators[i].hostname == missing)
            self.assertFalse(evaluators[i].platform == missing)
            self.assertTrue(evaluators[i].project_server_select == missing)
            self.assertTrue(evaluators[i].project_assignment_mode == missing)
            self.assertTrue(evaluators[i].external_access_port == missing)
            self.assertFalse(evaluators[i].configuration == missing)
            self.assertGreater(evaluators[i].configuration["system"]["num_cores"], 0)
            self.assertGreater(evaluators[i].configuration["system"]["memory"], 0)
            self.assertGreater(evaluators[i].configuration["max_num_parallel_tasks"], 0)
            self.assertGreater(len(evaluators[i].configuration["applications"]), 0)


if __name__ == "__main__":
    unittest.main()
