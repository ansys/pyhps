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


def test_dict_model_functionality():
    from ansys.hps.client.rms.models import EvaluatorResources, HpcResources

    obj = EvaluatorResources(
        num_cores=4,
        memory=1024,
        hpc_resources=HpcResources(
            queue="queue1",
            exclusive=True,
        ),
    )

    assert obj["num_cores"] == 4
    assert obj["hpc_resources"]["queue"] == "queue1"

    assert obj["hpc_resources"].get("num_cores_per_node", None) is None

    obj["hpc_resources"]["num_cores_per_node"] = 2
    assert obj["hpc_resources"].get("num_cores_per_node", None) == 2


def test_object_functionality():
    from ansys.hps.client.jms.resource.task_definition import HpcResources, ResourceRequirements

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
