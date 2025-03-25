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
# SOFTWARE.get_projects

import logging
import time

import pytest
import requests

from ansys.hps.client import Client
from ansys.hps.client.exceptions import HPSError

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


def test_authentication_username(url, username, password, keycloak_client):

    # Password workflow
    client0 = Client(url, username, password)
    assert client0.username == username

    # Impersonation
    realm_clients = keycloak_client.get_clients()
    rep_impersonation_client = next(
        (x for x in realm_clients if x["clientId"] == "rep-impersonation"), None
    )
    assert rep_impersonation_client is not None
    client1 = Client(
        url=url,
        client_id=rep_impersonation_client["clientId"],
        client_secret=rep_impersonation_client["secret"],
    )
    assert client1.username == "service-account-rep-impersonation"


def test_authentication_username_exception(url, username, keycloak_client):

    # Impersonation
    realm_clients = keycloak_client.get_clients()
    rep_impersonation_client = next(
        (x for x in realm_clients if x["clientId"] == "rep-impersonation"), None
    )
    assert rep_impersonation_client is not None
    with pytest.raises(HPSError):
        Client(
            url=url,
            username=username,
            client_id=rep_impersonation_client["clientId"],
            client_secret=rep_impersonation_client["secret"],
        )


def test_dt_client(url, username, password):
    client = Client(url, username, password)
    assert client._dt_client is None
    assert client._dt_api is None

    _ = client.data_transfer_api

    assert client._dt_client is not None
    assert client._dt_api is not None

    assert client.data_transfer_client == client._dt_client
    assert client.data_transfer_api == client._dt_api
