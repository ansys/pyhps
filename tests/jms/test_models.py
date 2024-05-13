# Copyright (C) 2022 - 2024 ANSYS, Inc. and/or its affiliates.
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

import json

from ansys.hps.client.jms.resource import HpcResources, Job, ResourceRequirements


def test_object_functionality():

    obj = ResourceRequirements(
        num_cores=4,
        memory=1024,
        hpc_resources=HpcResources(
            num_cores_per_node=2,
            queue="queue1",
            exclusive=True,
        ),
    )

    assert obj["num_cores"] == 4

    assert obj["hpc_resources"]["queue"] == "queue1"

    obj["hpc_resources"]["num_cores_per_node"] = 3
    assert obj["hpc_resources"].get("num_cores_per_node", None) == 3

    assert obj.get("memory") == 1024
    assert obj.get("service") is None


def test_serialization():

    obj = ResourceRequirements(
        num_cores=4,
        memory=1024,
        hpc_resources=HpcResources(
            num_cores_per_node=2,
            queue="queue1",
            exclusive=True,
        ),
    )

    obj_dict = obj.to_dict()

    assert obj_dict["num_cores"] == 4

    assert obj_dict["hpc_resources"]["queue"] == "queue1"

    obj_dict["hpc_resources"]["num_cores_per_node"] = 3
    assert obj_dict["hpc_resources"].get("num_cores_per_node", None) == 3

    assert obj_dict.get("memory") == 1024
    assert obj_dict.get("service") is None

    obj_json = obj.to_json()
    obj_dict = json.loads(obj_json)

    assert obj_dict["num_cores"] == 4

    assert obj_dict["hpc_resources"]["queue"] == "queue1"

    obj_dict["hpc_resources"]["num_cores_per_node"] = 3
    assert obj_dict["hpc_resources"].get("num_cores_per_node", None) == 3

    assert obj_dict.get("memory") == 1024
    assert obj_dict.get("service") is None


def test_serialization_load_only():
    # verify that load_only fields are not

    obj = Job(
        creation_time="2024-12-22T03:12:58.019077+00:00",
        name="job-name",
    )

    obj_dict = obj.to_dict()

    assert obj_dict["name"] == "job-name"
    assert "creation_time" not in obj_dict

    obj_json = obj.to_json()
    obj_dict = json.loads(obj_json)

    assert obj_dict["name"] == "job-name"
    assert "creation_time" not in obj_dict
