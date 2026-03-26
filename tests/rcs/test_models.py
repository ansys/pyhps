# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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
    from ansys.hps.client.rcs.models import RegisterInstance

    obj = RegisterInstance(
        url="http://example.com/hps/rcs",
        api_url="http://example.com/hps/rcs/api",
        service_name="service-123",
        jms_project_id="1234",
        jms_job_id="5678",
        jms_task_id="1011",
        routing="query",
    )

    assert obj["url"] == "http://example.com/hps/rcs"
    assert obj["service_name"] == "service-123"
    assert obj["jms_project_id"] == "1234"
    assert obj["jms_job_id"] == "5678"
    assert obj["jms_task_id"] == "1011"
    assert obj["routing"] == "query"
