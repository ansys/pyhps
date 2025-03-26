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
from unittest.mock import MagicMock, patch

import pytest
import requests

from ansys.hps.client import authenticate, determine_auth_url

log = logging.getLogger(__name__)


def test_authenticate(url, username, password):
    auth_url = determine_auth_url(hps_url=url, verify_ssl=False, fallback_realm="rep")
    resp = authenticate(auth_url=auth_url, username=username, password=password, verify=False)

    assert "access_token" in resp
    assert "refresh_token" in resp


def test_determine_auth_url_with_ssl_verification(url):
    with pytest.raises(requests.exceptions.SSLError) as ex_info:
        determine_auth_url(hps_url=url, verify_ssl=True, fallback_realm="rep")
    assert "CERTIFICATE_VERIFY_FAILED" in str(ex_info.value)


def test_authenticate_with_ssl_verification(url, username, password):
    auth_url = determine_auth_url(hps_url=url, verify_ssl=False, fallback_realm="rep")
    with pytest.raises(requests.exceptions.SSLError) as ex_info:
        _ = authenticate(auth_url=auth_url, username=username, password=password, verify=True)
    assert "CERTIFICATE_VERIFY_FAILED" in str(ex_info.value)


def test_determine_auth_url_success():
    hps_url = "https://example.com"
    verify_ssl = False
    fallback_realm = "rep"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "services": {"external_auth_url": "https://auth.example.com"}
    }

    with patch("requests.Session.get", return_value=mock_response):
        auth_url = determine_auth_url(hps_url, verify_ssl, fallback_realm)
        assert auth_url == "https://auth.example.com"


def test_determine_auth_url_fallback_realm():
    hps_url = "https://example.com"
    verify_ssl = False
    fallback_realm = "rep"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    with patch("requests.Session.get", return_value=mock_response):
        auth_url = determine_auth_url(hps_url, verify_ssl, fallback_realm)
        assert auth_url == f"{hps_url.rstrip('/')}/auth/realms/{fallback_realm}"


def test_determine_auth_url_no_realm():
    hps_url = "https://example.com"
    verify_ssl = False
    fallback_realm = None
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    with (
        patch("requests.Session.get", return_value=mock_response),
        patch("logging.Logger.warning") as mock_warning,
    ):
        auth_url = determine_auth_url(hps_url, verify_ssl, fallback_realm)
        assert auth_url is None
        mock_warning.assert_called_once_with(
            "External_auth_url not found from JMS and no realm specified."
        )


def test_determine_auth_url_failure():
    hps_url = "https://example.com"
    verify_ssl = False
    fallback_realm = "rep"
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.content.decode.return_value = "Internal Server Error"

    with (
        patch("requests.Session.get", return_value=mock_response),
        pytest.raises(RuntimeError) as ex_info,
    ):
        determine_auth_url(hps_url, verify_ssl, fallback_realm)
    assert "Failed to contact jms info endpoint" in str(ex_info.value)
    assert "status code 500" in str(ex_info.value)
    assert "Internal Server Error" in str(ex_info.value)
