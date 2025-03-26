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
import requests

from ansys.hps.client import Client, authenticate

log = logging.getLogger(__name__)


def test_authenticate(url, username, password):
    client = Client(url=url, username=username, password=password, verify=False)
    resp = authenticate(
        auth_url=client.auth_url, username=username, password=password, verify=False
    )

    assert "access_token" in resp
    assert "refresh_token" in resp


def test_authenticate_with_ssl_verification(url, username, password):
    # Doesn't matter that the auth url is wrong....  The first request will fail
    with pytest.raises(requests.exceptions.SSLError) as ex_info:
        _ = authenticate(
            auth_url=f"{url}/auth/realms/rep", username=username, password=password, verify=True
        )
    assert "CERTIFICATE_VERIFY_FAILED" in str(ex_info.value)
