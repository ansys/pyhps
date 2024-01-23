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
import json
import logging

from ansys.hps.client.rms.api.base import objects_to_json
from ansys.hps.client.rms.models import EvaluatorRegistration

log = logging.getLogger(__name__)


def test_serialize_objects_to_json():

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

