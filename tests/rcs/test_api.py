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

import re
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import portend
import pytest
import requests

from ansys.hps.client.rcs.api.base import create_object, delete_object
from ansys.hps.client.rcs.models import (
    RegisterInstance,
    RegisterInstanceResponse,
    UnRegisterInstance,
    UnRegisterInstanceResponse,
)


class HelloWorldHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/":
            # Respond with "Hello, World!"
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Hello, World!")
        else:
            # Respond with 404 for other paths
            self.send_response(404)
            self.end_headers()


@pytest.fixture(scope="module")
def http_server():
    port = portend.find_available_local_port()
    server = HTTPServer(("0.0.0.0", port), HelloWorldHandler)
    url = f"http://host.docker.internal:{port}"
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    yield server, url
    server.shutdown()
    thread.join()


def test_hello_world(http_server):
    server, url = http_server
    port = url.split(":")[-1]
    localhost_url = f"http://localhost:{port}"
    response = requests.get(localhost_url)
    assert response.status_code == 200
    assert response.text == "Hello, World!"


def test_health_check(rcs_api, has_hps_version_le_1_3_45):
    """Test the health_check method."""
    if has_hps_version_le_1_3_45:
        pytest.skip("RCS was introduced after HPS v1.3.45.")
    response = rcs_api.health_check()
    # Assert
    assert response["status"] == "alive"


def test_register_instance_and_response(rcs_api, http_server, has_hps_version_le_1_3_45):
    """Test the register_instance method and RegisterInstanceResponse model."""

    if has_hps_version_le_1_3_45:
        pytest.skip("RCS was introduced after HPS v1.3.45.")

    server, url = http_server
    print(f"url is {url}")
    # Arrange
    instance_data = RegisterInstance(
        url=url,
        service_name="test_service",
        jms_project_id="1234",
        jms_job_id="5678",
        jms_task_id="91011",
        routing="path_prefix",
    )

    # Act
    response = rcs_api.register_instance(instance_data)

    # Assert RegisterInstanceResponse
    assert isinstance(response, RegisterInstanceResponse)
    uid = (response.resource_name).split("-")[-1]
    expected_url_pattern = rf".*/ans_instance_id/{uid}"
    assert re.match(expected_url_pattern, response.instance_url), (
        f"URL '{response.instance_url}' does not match the expected pattern "
        f"'{expected_url_pattern}'"
    )
    assert response.resource_name == f"test_service-{uid}"

    url = f"https://{response.instance_url}"
    res = requests.get(url, verify=False)
    # Assert the instance is accessible at the registered URL
    print(f"url is {url}")
    # import time
    # time.sleep(1000)
    assert res.status_code == 200
    assert res.text == "Hello, World!"

    expected_response_data = {
        "message": f"Successfully unregistered {response.resource_name} "
        "from Redis. Deleted 4 keys.",
        "resource_name": response.resource_name,
    }
    # Act
    unregister_instance = UnRegisterInstance(resource_name=response.resource_name)
    response = rcs_api.unregister_instance(unregister_instance)

    # Assert UnRegisterInstanceResponse
    assert isinstance(response, UnRegisterInstanceResponse)
    assert response.message == expected_response_data["message"]
    assert response.resource_name == expected_response_data["resource_name"]


def test_create_objects_as_objects_false(client, url, http_server, has_hps_version_le_1_3_45):
    """Test the create_object function with as_object=False."""
    if has_hps_version_le_1_3_45:
        pytest.skip("RCS was introduced after HPS v1.3.45.")

    server, instance_url = http_server
    # Arrange
    obj = RegisterInstance(
        url=instance_url,
        service_name="service-123",
        routing="path_prefix",
    )

    # Act
    result = create_object(
        session=client.session,
        url=url + "/rcs",
        object=obj,
        as_object=False,
    )

    assert isinstance(result, dict)
    uid = (result["resource_name"]).split("-")[-1]
    expected_url_pattern = rf".*/ans_instance_id/{uid}"
    res_url = result["instance_url"]
    assert re.match(expected_url_pattern, res_url), (
        f"URL '{res_url}' does not match the expected pattern '{expected_url_pattern}'"
    )
    assert result["resource_name"] == f"service-123-{uid}"

    unreg_obj = UnRegisterInstance(resource_name=result["resource_name"])
    delete_result = delete_object(
        session=client.session,
        url=url + "/rcs",
        object=unreg_obj,
        as_object=False,
    )
    assert isinstance(delete_result, dict)
    expected_delete_response = {
        "message": f"Successfully unregistered {result['resource_name']} "
        "from Redis. Deleted 4 keys.",
        "resource_name": result["resource_name"],
    }
    assert delete_result == expected_delete_response
