import datetime
import json
import logging
import unittest

from ansys.hps.client.rms.api.base import objects_to_json
from ansys.hps.client.rms.models import EvaluatorRegistration
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class RmsSerializationTest(REPTestCase):
    def test_serialize_objects_to_json(self):

        num_evals = 10
        evaluator_objects = [
            EvaluatorRegistration(
                id="02q1DiPEP0nanLN5384q8L",
                host_name=f"machine{i}",
                host_id="db337a96-ebbb-362a-8c02",
                name=f"eval_{i}",
                username="repuser",
                last_modified=datetime.datetime(2023, 11, 20, 9, 41, i),
                build_info={
                    "version": f"1.0.{i}",
                    "latest": True,
                },
            )
            for i in range(num_evals)
        ]

        json_data = objects_to_json(evaluator_objects, "evaluators")
        data = json.loads(json_data)
        assert "evaluators" in data
        data = data["evaluators"]
        assert len(data) == num_evals
        assert data[0]["host_name"] == "machine0"
        assert data[0]["host_id"] == "db337a96-ebbb-362a-8c02"
        assert data[8]["host_name"] == "machine8"
        assert data[7]["last_modified"] == "2023-11-20T09:41:07"
        assert data[6]["build_info"]["version"] == "1.0.6"
        assert data[6]["build_info"]["latest"] == True


if __name__ == "__main__":
    unittest.main()
