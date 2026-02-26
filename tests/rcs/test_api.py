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

from unittest.mock import MagicMock

import pytest

from ansys.hps.client.rcs.api.rcs_api import RcsApi
from ansys.hps.client.rcs.models import (
    RegisterInstance,
    RegisterInstanceResponse,
    UnRegisterInstance,
    UnRegisterInstanceResponse,
)


@pytest.fixture
def mock_client():
    """Fixture to create a mock client."""
    client = MagicMock()
    client.url = "http://mockserver"
    client.session = MagicMock()
    return client


@pytest.fixture
def rcs_api(mock_client):
    """Fixture to create an RcsApi instance."""
    return RcsApi(mock_client)


def test_health_check(rcs_api, mock_client):
    """Test the health_check method."""
    # Mock the response from the API
    mock_client.session.get.return_value.json.return_value = {"status": "healthy"}

    # Act
    response = rcs_api.health_check()

    # Assert
    assert response["status"] == "healthy"


def test_register_instance_and_response(rcs_api, mock_client):
    """Test the register_instance method and RegisterInstanceResponse model."""
    # Arrange
    mock_data = RegisterInstance(
        url="http://example.com",
        service_name="test_service",
        jms_project_id="1234",
        jms_job_id="5678",
        jms_task_id="91011",
        routing="path_prefix",
    )

    mock_response_data = {
        "instance_url": "http://example.com/instance",
        "resource_name": "test_resource",
    }
    mock_client.session.post.return_value.json.return_value = mock_response_data

    # Act
    response = rcs_api.register_instance(mock_data)

    # Assert RegisterInstanceResponse
    assert isinstance(response, RegisterInstanceResponse)
    assert response.instance_url == mock_response_data["instance_url"]
    assert response.resource_name == mock_response_data["resource_name"]

    # Assert RegisterInstance
    assert mock_data.url == "http://example.com"
    assert mock_data.service_name == "test_service"
    assert mock_data.jms_project_id == "1234"
    assert mock_data.jms_job_id == "5678"
    assert mock_data.jms_task_id == "91011"
    assert mock_data.routing == "path_prefix"


def test_unregister_instance_and_response(rcs_api, mock_client):
    """Test the unregister_instance method and UnRegisterInstanceResponse model."""
    # Arrange
    resource_name = "test_resource"

    mock_response_data = {
        "message": "Instance successfully unregistered",
        "resource_name": resource_name,
    }
    mock_client.session.delete.return_value.json.return_value = mock_response_data

    # Act
    unregister_instance = UnRegisterInstance(resource_name=resource_name)
    response = rcs_api.unregister_instance(unregister_instance)

    # Assert UnRegisterInstanceResponse
    assert isinstance(response, UnRegisterInstanceResponse)
    assert response.message == mock_response_data["message"]
    assert response.resource_name == mock_response_data["resource_name"]

    # Assert UnRegisterInstance
    assert unregister_instance.resource_name == resource_name
