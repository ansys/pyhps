# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
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

import logging

import pytest
from ansys.hps.client import APIError, Client, ClientError
from ansys.hps.client.jms import JmsApi

log = logging.getLogger(__name__)


def test_server_error(client):
    jms_api = JmsApi(client)
    except_obj = None
    try:
        jms_api.get_projects(wrong_query_param="value")
    except APIError as e:
        except_obj = e
        log.error(str(e))

    assert except_obj.reason == "500 Internal Server Error"
    assert except_obj.description == "type object 'Project' has no attribute 'wrong_query_param'"
    assert except_obj.response.status_code == 500


@pytest.mark.xfail
def test_client_error(url, username, password, client):
    except_obj = None
    try:
        client = Client(url, username, f"{password}_wrong")
    except ClientError as e:
        except_obj = e
        log.error(str(e))

    assert except_obj.reason == "invalid_grant"
    assert except_obj.description == "Invalid user credentials"
    assert except_obj.response.status_code == 401

    except_obj = None
    try:
        jms_api = JmsApi(client)
        jms_api.get_project(id="02q4bg9PVO2OvvhsmClb0E")
    except ClientError as e:
        except_obj = e
        log.error(str(e))

    # The answer that one would expect:
    # self.assertEqual(except_obj.reason, 'Not Found')
    # self.assertEqual(except_obj.response.status_code, 404)
    # The answer currently received when querying this with a user different from repadmin
    assert except_obj.reason == "404 Not Found"
    assert except_obj.response.status_code == 404
