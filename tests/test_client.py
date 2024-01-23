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
# SOFTWARE.get_projects

import logging
import time

import requests
import pytest

from ansys.hps.client import Client

log = logging.getLogger(__name__)


def test_client_ssl_warning(url, username, password):
    with pytest.warns(Warning) as record:
        _ = Client(url, username, password)
    assert len(record) == 1
    assert "Unverified HTTPS requests" in str(record[0].message)

def test_client_with_ssl_verification(url, username, password):
    with pytest.raises(requests.exceptions.SSLError) as ex_info:
        _ = Client(url, username, password, verify=True)
    assert "CERTIFICATE_VERIFY_FAILED" in str(ex_info.value)

def test_authentication_workflows(url, username, password):

    ## Auth with user and password
    client0 = Client(url, username, password)

    assert client0.access_token is not None
    assert client0.refresh_token is not None

    access_token0 = client0.access_token
    refresh_token0 = client0.refresh_token

    # wait a moment otherwise the OAuth server will issue the very same tokens
    time.sleep(0.5)

    client0.refresh_access_token()
    assert client0.access_token != access_token0
    assert client0.refresh_token != refresh_token0

    ## Auth with access token
    client1 = Client(url, access_token=client0.access_token)
    assert client1.access_token == client0.access_token
    assert client1.refresh_token is None

    ## Auth with refresh token
    client2 = Client(
        url,
        refresh_token=client0.refresh_token,
        username=client0.username,
    )
    assert client2.access_token is not None
    assert client2.refresh_token != client0.refresh_token
    client2.refresh_access_token()
