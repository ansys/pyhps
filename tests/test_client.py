# Copyright (C) 2022 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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
import threading
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest
import requests

from ansys.hps.client import Client
from ansys.hps.client.exceptions import HPSError
from ansys.hps.client.warnings import UnverifiedHTTPSRequestsWarning

log = logging.getLogger(__name__)


def _build_client_with_mocked_auth(**kwargs):
    """Create a Client while mocking network/auth dependencies."""
    token_response = {
        "access_token": "mock_access_token",
        "refresh_token": "mock_refresh_token",
        "expires_in": 3600,
        "refresh_expires_in": 86400,
    }

    mock_session = Mock()
    mock_session.headers = {"Authorization": "Bearer mock_access_token"}
    mock_session.hooks = {}
    mock_session.params = {}

    with patch(
        "ansys.hps.client.client.determine_auth_url", return_value="https://auth.test/realm"
    ):
        with patch("ansys.hps.client.client.authenticate", return_value=token_response):
            with patch(
                "ansys.hps.client.client.jwt.decode",
                return_value={"preferred_username": kwargs.get("username", "repadmin")},
            ):
                with patch("ansys.hps.client.client.create_session", return_value=mock_session):
                    return Client(
                        url="https://example.test/hps",
                        username=kwargs.get("username", "repadmin"),
                        password=kwargs.get("password", "repadmin"),
                        verify=False,
                        disable_security_warnings=True,
                        auto_refresh_token=False,
                        **{k: v for k, v in kwargs.items() if k not in {"username", "password"}},
                    )


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


def test_external_tokens_seed_refresh_schedule(url, username, password):
    """Externally supplied access+refresh tokens should schedule preemptive refresh."""
    source_client = Client(url, username, password)

    client = Client(
        url,
        access_token=source_client.access_token,
        refresh_token=source_client.refresh_token,
        auto_refresh_token=False,
    )

    assert client.token_expires_in is not None
    assert client.token_acquired_date is not None
    assert client.token_refresh_date is not None


def test_refresh_access_token_persists_to_disk(url, username, password):
    """Refreshed tokens should be persisted when token_storage is disk."""
    client = Client(url, username, password, token_storage="disk")

    with patch("ansys.hps.client.common.token_storage.save_tokens") as mock_save_tokens:
        client.refresh_access_token()

    mock_save_tokens.assert_called_once()
    _, called_url = mock_save_tokens.call_args[0]
    assert called_url == url
    assert mock_save_tokens.call_args.kwargs["storage"] == "disk"


def test_refresh_access_token_persists_to_keyring(url, username, password):
    """Refreshed tokens should be persisted when token_storage is keyring."""
    client = Client(url, username, password, token_storage="keyring")

    with patch("ansys.hps.client.common.token_storage.save_tokens") as mock_save_tokens:
        client.refresh_access_token()

    mock_save_tokens.assert_called_once()
    _, called_url = mock_save_tokens.call_args[0]
    assert called_url == url
    assert mock_save_tokens.call_args.kwargs["storage"] == "keyring"


def test_refresh_access_token_rotation_is_persisted(url, username, password):
    """Rotated refresh tokens should be persisted after refresh."""
    client = Client(url, username, password, token_storage="keyring")
    old_refresh_token = client.refresh_token
    rotated_refresh_token = "rotated_refresh_token_value"

    refreshed_tokens = {
        "access_token": client.access_token,
        "refresh_token": rotated_refresh_token,
        "expires_in": 3600,
        "refresh_expires_in": 86400,
    }

    with patch("ansys.hps.client.client.authenticate", return_value=refreshed_tokens):
        with patch("ansys.hps.client.common.token_storage.save_tokens") as mock_save_tokens:
            client.refresh_access_token()

    assert client.refresh_token == rotated_refresh_token
    assert client.refresh_token != old_refresh_token
    saved_tokens, saved_url = mock_save_tokens.call_args[0]
    assert saved_url == url
    assert saved_tokens["refresh_token"] == rotated_refresh_token
    assert mock_save_tokens.call_args.kwargs["storage"] == "keyring"


def test_refresh_access_token_raises_when_refresh_token_missing():
    """Refresh flow fails fast when no refresh token is available."""
    client = _build_client_with_mocked_auth()
    client.grant_type = "refresh_token"
    client.refresh_token = None

    with pytest.raises(HPSError, match="No refresh token available"):
        client.refresh_access_token()


def test_refresh_access_token_persistence_result_keyring_failure_uses_memory_only(
    url, username, password
):
    """Telemetry should report memory-only behavior when keyring persistence fails."""
    client = Client(url, username, password, token_storage="keyring")

    with patch(
        "ansys.hps.client.common.token_storage.save_tokens",
        side_effect=RuntimeError("keyring unavailable"),
    ):
        client.refresh_access_token()

    assert client.last_token_persistence_result is not None
    assert client.last_token_persistence_result["requested_storage"] == "keyring"
    assert client.last_token_persistence_result["storage_used"] == "memory"
    assert client.last_token_persistence_result["fallback_used"] is False
    assert client.last_token_persistence_result["persisted"] is False
    assert client.last_token_persistence_result["error"] == "keyring unavailable"


def test_refresh_access_token_persistence_result_failure_uses_memory_only(url, username, password):
    """Telemetry should report persistence failures with memory-only behavior."""
    client = Client(url, username, password, token_storage="disk")

    with patch(
        "ansys.hps.client.common.token_storage.save_tokens",
        side_effect=RuntimeError("persistence failed"),
    ):
        client.refresh_access_token()

    assert client.last_token_persistence_result is not None
    assert client.last_token_persistence_result["requested_storage"] == "disk"
    assert client.last_token_persistence_result["storage_used"] == "memory"
    assert client.last_token_persistence_result["persisted"] is False
    assert client.last_token_persistence_result["error"] == "persistence failed"


def test_refresh_access_token_persistence_logs_are_redacted(url, username, password, caplog):
    """Persistence failures must not log raw token values."""
    client = Client(url, username, password, token_storage="disk")
    leaked_error = (
        f"persistence failed access={client.access_token} "
        f"refresh={client.refresh_token} bearer=Bearer {client.access_token}"
    )

    caplog.set_level(logging.WARNING, logger="ansys.hps.client.client")
    with patch(
        "ansys.hps.client.common.token_storage.save_tokens",
        side_effect=RuntimeError(leaked_error),
    ):
        client.refresh_access_token()

    assert client.access_token not in caplog.text
    assert client.refresh_token not in caplog.text
    assert "Bearer " + client.access_token not in caplog.text
    assert "***REDACTED***" in caplog.text

    err = client.last_token_persistence_result["error"]
    assert client.access_token not in err
    assert client.refresh_token not in err
    assert "Bearer " + client.access_token not in err
    assert "***REDACTED***" in err


def test_token_storage_keyring_warns_when_backend_unavailable(caplog):
    """Keyring storage should log a warning when backend is unavailable in non-strict mode."""
    with patch(
        "ansys.hps.client.common.token_storage._check_storage_backend",
        side_effect=lambda storage: "backend unavailable" if storage == "keyring" else None,
    ):
        with caplog.at_level(logging.WARNING, logger="ansys.hps.client.client"):
            client = _build_client_with_mocked_auth(token_storage="keyring")
    assert "Keyring token storage requested but unavailable" in caplog.text
    assert client.token_storage == "keyring"


def test_token_storage_keyring_strict_raises_when_backend_unavailable():
    """Strict mode should fail fast when keyring backend is unavailable."""
    with patch(
        "ansys.hps.client.common.token_storage._check_storage_backend",
        side_effect=lambda storage: "backend unavailable" if storage == "keyring" else None,
    ):
        with pytest.raises(RuntimeError, match="Keyring token storage requested but unavailable"):
            _build_client_with_mocked_auth(
                token_storage="keyring",
                token_storage_strict=True,
            )


def test_token_storage_disk_warns_when_backend_unavailable(caplog):
    """Disk storage should log a warning when backend is unavailable in non-strict mode."""
    with patch(
        "ansys.hps.client.common.token_storage._check_storage_backend",
        side_effect=lambda storage: "disk unavailable" if storage == "disk" else None,
    ):
        with caplog.at_level(logging.WARNING, logger="ansys.hps.client.client"):
            client = _build_client_with_mocked_auth(token_storage="disk")
    assert "Disk token storage requested but unavailable" in caplog.text
    assert client.token_storage == "disk"


def test_token_storage_disk_strict_raises_when_backend_unavailable():
    """Strict mode should fail fast when disk backend is unavailable."""
    with patch(
        "ansys.hps.client.common.token_storage._check_storage_backend",
        side_effect=lambda storage: "disk unavailable" if storage == "disk" else None,
    ):
        with pytest.raises(RuntimeError, match="Disk token storage requested but unavailable"):
            _build_client_with_mocked_auth(
                token_storage="disk",
                token_storage_strict=True,
            )


def test_reschedule_after_failed_refresh(url, username, password):
    """Failed refreshes must escalate through retry factors, then give up."""
    client = Client(url, username, password)

    # Stop the background thread so it doesn't race with our manipulations.
    client._stop_event.set()
    client._token_refresh_thread.join(timeout=5)

    acquired = client.token_acquired_date
    expires_in = client.token_expires_in
    retry_factors = client.token_refresh_retry_factors
    assert len(retry_factors) > 0

    err = RuntimeError("simulated refresh failure")

    # Each failure should reschedule at the next retry factor.
    for i, factor in enumerate(retry_factors, start=1):
        client._reschedule_after_failed_refresh(err)
        assert client._refresh_attempt == i
        expected_offset = max(1, int(expires_in * factor))
        expected_date = acquired + timedelta(seconds=expected_offset)
        assert client.token_refresh_date == expected_date

    # One more failure exhausts the retries and disables preemptive refresh.
    client._reschedule_after_failed_refresh(err)
    assert client.token_refresh_date is None


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
    client.token_refresh_date = datetime.now(timezone.utc) - timedelta(seconds=1)
    client._start_token_refresh_thread()

    # Wait for the background thread to perform the refresh
    deadline = time.time() + 5
    while time.time() < deadline and client.access_token == initial_access_token:
        time.sleep(0.1)

    assert client.access_token != initial_access_token
    assert client.token_refresh_date > datetime.now(timezone.utc)
