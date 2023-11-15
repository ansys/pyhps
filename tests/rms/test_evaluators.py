import logging
import unittest

from ansys.rep.client.rms import RmsApi
from ansys.rep.client.rms.models import EvaluatorRegistration
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)

missing = None


class EvaluatorTest(REPTestCase):
    def test_evaluator_deserialization(self):

        evaluator_dict = {
            "project_server_select": True,
            # "alive_update_interval": 15,
            "id": "02q1DiPEP0nanLN5384q8L",
            # "last_modified": "2019-05-07T05:42:52.493419+00:00",
            "project_assignment_mode": "all_active",
            # "platform": "Windows",
            "task_manager_type": "Direct",
            "hostname": "dc_evaluator_win10_2019R3_tmp",
            "host_id": "db337a96-ebbb-362a-8c02-1103c15e2b43",
            "name": "dc_evaluator_win10_2019R3_tmp",
            "external_access_port": 443,
            "username": "repuser",
        }

        evaluator = EvaluatorRegistration(**evaluator_dict)

        self.assertEqual(evaluator.__class__.__name__, "EvaluatorRegistration")
        self.assertEqual(evaluator.platform, missing)
        self.assertEqual(evaluator.last_modified, missing)
        self.assertEqual(evaluator.name, evaluator_dict["name"])

        evaluator_dict["project_assignment_mode"] = "project_list"

        evaluator = EvaluatorRegistration(**evaluator_dict)
        self.assertEqual(evaluator.project_assignment_mode, "project_list")
        self.assertEqual(len(evaluator.project_list), 2)
        self.assertEqual(evaluator.project_list[1], "proj2")

    def test_evaluator_integration(self):

        client = self.client
        rms_api = RmsApi(client)
        evaluators = rms_api.get_evaluators()

        if evaluators:
            self.assertTrue(evaluators[0].id is not None)

        evaluators = rms_api.get_evaluators(as_objects=False)
        if evaluators:
            self.assertTrue(evaluators[0]["id"] is not None)

        evaluators = rms_api.get_evaluators(
            as_objects=False, fields=["host_name", "platform", "username"]
        )

        if evaluators:
            self.assertTrue("host_name" in evaluators[0].keys())
            self.assertTrue("platform" in evaluators[0].keys())
            self.assertTrue("username" in evaluators[0].keys())

        evaluators = rms_api.get_evaluators(fields=["host_name", "platform"])

        for ev in evaluators:
            self.assertFalse(ev.host_name == missing)
            self.assertFalse(ev.platform == missing)


if __name__ == "__main__":
    unittest.main()
