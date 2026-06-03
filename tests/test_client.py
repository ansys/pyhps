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
# SOFTWARE.get_projects

import logging
import threading
import time

import arrow
import pytest
import requests

from ansys.hps.client import Client
from ansys.hps.client.exceptions import HPSError
from ansys.hps.client.warnings import UnverifiedHTTPSRequestsWarning

log = logging.getLogger(__name__)


def test_client_ssl_warning(url, username, password):
    with pytest.warns(UnverifiedHTTPSRequestsWarning) as record:
        _ = Client(url, username, password)
    assert any("Unverified HTTPS requests" in str(w.message) for w in record)


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


def test_update_token_expiry_sets_refresh_date(url, username, password):
    """After authentication, expiry-related fields must be populated."""
    client = Client(url, username, password)

    assert client.token_expires_in is not None
    assert client.token_acquired_date is not None
    assert client.token_refresh_date is not None
    # refresh date should be in the future and within token lifetime
    assert client.token_refresh_date > client.token_acquired_date
    diff = (client.token_refresh_date - client.token_acquired_date).total_seconds()
    assert 0 < diff <= client.token_expires_in


def test_update_token_expiry_updates_after_refresh(url, username, password):
    """Calling refresh_access_token must move token_refresh_date forward."""
    client = Client(url, username, password)
    first_refresh_date = client.token_refresh_date

    time.sleep(0.5)
    client.refresh_access_token()

    assert client.token_refresh_date > first_refresh_date


def test_periodically_refresh_token_refreshes_preemptively(url, username, password):
    """The background thread must refresh the access token before it expires."""
    client = Client(url, username, password)
    initial_access_token = client.access_token

    # The background thread is already sleeping with the default loop_interval
    # against a fresh token_refresh_date. Stop it, retune the schedule so a
    # refresh is due immediately, then restart so the new values take effect.
    client._stop_event.set()
    client._token_refresh_thread.join(timeout=5)
    client._stop_event = threading.Event()
    client._token_refresh_thread = None
    client.loop_interval = 0.1
    client.token_refresh_date = arrow.now().shift(seconds=-1)
    client._start_token_refresh_thread()

    # Wait for the background thread to perform the refresh
    deadline = time.time() + 5
    while time.time() < deadline and client.access_token == initial_access_token:
        time.sleep(0.1)

    assert client.access_token != initial_access_token
    assert client.token_refresh_date > arrow.now()
