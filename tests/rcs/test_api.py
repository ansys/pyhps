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

import pytest
import requests

from ansys.hps.client.rcs.api.base import create_object
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
    server = HTTPServer(("localhost", 8000), HelloWorldHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    yield server
    server.shutdown()
    thread.join()


def test_hello_world(http_server):
    response = requests.get("http://localhost:8000/")
    assert response.status_code == 200
    assert response.text == "Hello, World!"


@pytest.fixture(scope="module")
def resource_name():
    """Fixture to store and share the resource name."""
    return {"value": None}


def test_health_check(rcs_api):
    """Test the health_check method."""
    response = rcs_api.health_check()
    # Assert
    assert response["status"] == "alive"


def test_register_instance_and_response(rcs_api, http_server, resource_name):
    """Test the register_instance method and RegisterInstanceResponse model."""
    # Arrange
    mock_data = RegisterInstance(
        url="http://localhost:8000/",
        service_name="test_service",
        jms_project_id="1234",
        jms_job_id="5678",
        jms_task_id="91011",
        routing="path_prefix",
    )

    # Act
    response = rcs_api.register_instance(mock_data)

    # Assert RegisterInstanceResponse
    assert isinstance(response, RegisterInstanceResponse)
    uid = (response.resource_name).split("-")[-1]
    expected_url_pattern = rf".*/ans_instance_id/{uid}"
    assert re.match(expected_url_pattern, response.instance_url), (
        f"URL '{response.instance_url}' does not match the expected pattern "
        f"'{expected_url_pattern}'"
    )
    assert response.resource_name == f"test_service-{uid}"

    # Save the resource name in the fixture
    resource_name["value"] = response.resource_name

    # Assert the instance is accessible at the registered URL
    test_hello_world(http_server)

    # Assert RegisterInstance
    assert mock_data.url == "http://localhost:8000/"
    assert mock_data.service_name == "test_service"
    assert mock_data.jms_project_id == "1234"
    assert mock_data.jms_job_id == "5678"
    assert mock_data.jms_task_id == "91011"
    assert mock_data.routing == "path_prefix"


def test_unregister_instance_and_response(rcs_api, resource_name):
    """Test the unregister_instance method and UnRegisterInstanceResponse model."""
    # Arrange
    unregister_resource_name = resource_name["value"]  # Access the resource name from the fixture

    mock_response_data = {
        "message": f"Successfully unregistered {unregister_resource_name} "
        "from Redis. Deleted 4 keys.",
        "resource_name": unregister_resource_name,
    }
    # Act
    unregister_instance = UnRegisterInstance(resource_name=unregister_resource_name)
    response = rcs_api.unregister_instance(unregister_instance)

    # Assert UnRegisterInstanceResponse
    assert isinstance(response, UnRegisterInstanceResponse)
    assert response.message == mock_response_data["message"]
    assert response.resource_name == mock_response_data["resource_name"]

    # Assert UnRegisterInstance
    assert unregister_instance.resource_name == unregister_resource_name


def test_create_objects_as_objects_false(client, url, http_server):
    """Test the create_object function with as_object=False."""
    # Arrange
    obj = RegisterInstance(
        url="http://localhost:8000/",
        api_url="http://localhost:8000/api",
        service_name="service-123",
        jms_project_id="1234",
        jms_job_id="5678",
        jms_task_id="1011",
        routing="path_prefix",
    )

    # Act
    result = create_object(
        session=client.session,
        url=url + "/rcs",
        object=obj,
        as_object=False,
    )

    print(result)

    assert isinstance(result, dict)
    uid = (result["resource_name"]).split("-")[-1]
    expected_url_pattern = rf".*/ans_instance_id/{uid}"
    url = result["instance_url"]
    assert re.match(expected_url_pattern, url), (
        f"URL '{url}' does not match the expected pattern '{expected_url_pattern}'"
    )
    assert result["resource_name"] == f"service-123-{uid}"
