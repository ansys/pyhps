# Copyright (C) 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import datetime
import logging
import unittest

from ansys.hps.core.rms import RmsApi
from ansys.hps.core.rms.models import EvaluatorConfigurationUpdate, EvaluatorRegistration
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class EvaluatorTest(REPTestCase):
    def test_evaluator_deserialization(self):

        evaluator_dict = {
            "id": "02q1DiPEP0nanLN5384q8L",
            # "last_modified": "2019-05-07T05:42:52.493419+00:00",
            # "platform": "Windows",
            "host_name": "dc_evaluator_win10_2019R3_tmp",
            "host_id": "db337a96-ebbb-362a-8c02-1103c15e2b43",
            "name": "dc_evaluator_win10_2019R3_tmp",
            "username": "repuser",
        }

        evaluator = EvaluatorRegistration(**evaluator_dict)

        self.assertEqual(evaluator.__class__.__name__, "EvaluatorRegistration")
        self.assertIsNone(evaluator.platform)
        self.assertIsNone(evaluator.last_modified)
        self.assertEqual(evaluator.name, evaluator_dict["name"])

    def test_evaluator_integration(self):

        client = self.client
        rms_api = RmsApi(client)
        evaluators = rms_api.get_evaluators(limit=1000)

        if evaluators:
            log.debug(f"Found {len(evaluators)} evaluators")
            assert evaluators[0].id is not None

        num_evals = rms_api.get_evaluators_count(limit=1000)
        assert num_evals == len(evaluators)

        evaluators = rms_api.get_evaluators(as_objects=False)
        if evaluators:
            assert evaluators[0]["id"] is not None

        evaluators = rms_api.get_evaluators(
            as_objects=False, fields=["host_name", "platform", "username"]
        )

        if evaluators:
            assert "host_name" in evaluators[0].keys()
            assert "platform" in evaluators[0].keys()
            assert "username" in evaluators[0].keys()

        evaluators = rms_api.get_evaluators(fields=["host_name", "platform"])

        for ev in evaluators:
            self.assertFalse(ev.host_name is None)
            self.assertFalse(ev.platform is None)

            config = rms_api.get_evaluator_configuration(ev.id)
            self.assertGreater(config.resources.num_cores, 0)
            self.assertIsNotNone(config.resources.memory)
            self.assertGreater(config.max_num_parallel_tasks, 0)
            self.assertIsNotNone(config.applications, 0)

    def test_evaluator_configuration_update(self):
        client = self.client
        rms_api = RmsApi(client)
        query_params = {
            "last_modified.gt": datetime.datetime.utcnow() - datetime.timedelta(seconds=20)
        }
        evaluators = rms_api.get_evaluators(**query_params)

        if len(evaluators) == 0:
            self.skipTest(f"This test requires running evaluators.")

        ev = evaluators[0]
        config_update = EvaluatorConfigurationUpdate(loop_interval=4)
        config_update_response = rms_api.update_evaluator_configuration(ev.id, config_update)
        assert config_update_response.loop_interval == 4


if __name__ == "__main__":
    unittest.main()
