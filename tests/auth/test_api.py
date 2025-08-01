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
import uuid
from unittest.mock import MagicMock

import pytest
from keycloak import KeycloakOpenID

from ansys.hps.client import Client, ClientError, HPSError, authenticate
from ansys.hps.client.auth import AuthApi, User
from tests.utils import create_user, delete_user

log = logging.getLogger(__name__)


def test_get_users(client, keycloak_client):
    api = AuthApi(client)

    assert "rep" in api.realm_url

    # create a new non-admin user
    username = f"test_user_{uuid.uuid4()}"
    first_name = f"Test-{uuid.uuid4()}"
    new_user = User(
        username=username,
        password="test_auth_client",
        email=f"{username}@test.com",
        first_name=first_name,
        last_name="User",
    )
    new_user = create_user(keycloak_client, new_user)
    assert new_user.first_name == first_name
    users = api.get_users(max=10)

    # use non-admin user to get users
    api_non_admin = AuthApi(Client(client.url, username=username, password="test_auth_client"))
    users2 = api_non_admin.get_users(max=10)
    assert len(users) == len(users2)

    users_with_test_name = api_non_admin.get_users(firstName=first_name)
    assert len(users_with_test_name) == 1

    new_user2 = api.get_user(new_user.id)
    assert new_user == new_user2

    delete_user(keycloak_client, new_user)
    users = api.get_users(username=new_user.username)
    assert len(users) == 0

    with pytest.raises(ClientError) as ex_info:
        api.get_user(new_user.id)

    assert ex_info.value.response.status_code == 404


def test_get_user_permissions(client):
    api = AuthApi(client)

    user = api.get_users(username=client.username)[0]

    groups = api.get_user_groups(user.id)
    for g in groups:
        assert g is not None
        assert isinstance(g, dict)

    roles = api.get_user_realm_roles(user.id)
    for r in roles:
        assert r is not None
        assert isinstance(r, dict)

    groups = api.get_user_groups_names(user.id)
    for g in groups:
        assert g is not None
        assert isinstance(g, str)

    roles = api.get_user_realm_roles_names(user.id)
    for r in roles:
        assert r is not None
        assert isinstance(r, str)

    assert api.user_is_admin is not None


def test_impersonate_user(url, keycloak_client):
    """Test token exchange for impersonation, see https://www.rfc-editor.org/rfc/rfc8693.html.

    Requires activating the token-exchange feature in keycloak
    by passing --features=token-exchange to the start command.
    """
    username = f"test_user_{uuid.uuid4()}"
    new_user = User(
        username=username,
        password="test_auth_client",
        email=f"{username}@test.com",
        first_name="Test",
        last_name="User",
    )
    new_user = create_user(keycloak_client, new_user)

    realm_clients = keycloak_client.get_clients()
    rep_impersonation_client = next(
        (x for x in realm_clients if x["clientId"] == "rep-impersonation"), None
    )
    assert rep_impersonation_client is not None

    client = Client(
        url=url,
        client_id=rep_impersonation_client["clientId"],
        client_secret=rep_impersonation_client["secret"],
    )

    r = None
    try:
        r = authenticate(
            auth_url=client.auth_url,
            client_id=rep_impersonation_client["clientId"],
            client_secret=rep_impersonation_client["secret"],
            scope="openid offline_access",
            grant_type="urn:ietf:params:oauth:grant-type:token-exchange",
            subject_token=client.access_token,
            requested_token_type="urn:ietf:params:oauth:token-type:refresh_token",
            requested_subject=new_user.id,
            verify=False,
        )
    except HPSError as e:
        log.error(e)
        if e.response.status_code == 501 and "Feature not enabled" in e.reason:
            pytest.skip("This test requires to enable the feature 'token-exchange' in keycloak.")

    assert r is not None
    assert "refresh_token" in r

    refresh_token_impersonated = r["refresh_token"]

    client_impersonated = Client(
        url,
        username=new_user.username,
        grant_type="refresh_token",
        refresh_token=refresh_token_impersonated,
        client_id=rep_impersonation_client["clientId"],
        client_secret=rep_impersonation_client["secret"],
    )

    assert client_impersonated.access_token is not None
    assert client_impersonated.refresh_token is not None

    keycloak_openid = KeycloakOpenID(
        server_url=client.auth_api_url,
        client_id="account",
        realm_name="rep",
        client_secret_key="**********",
        verify=False,
    )
    keycloak_public_key = "-----BEGIN PUBLIC KEY-----\n"
    keycloak_public_key += keycloak_openid.public_key()
    keycloak_public_key += "\n-----END PUBLIC KEY-----"

    options = {"verify_signature": True, "verify_aud": True, "verify_exp": True}
    token_info = keycloak_openid.decode_token(
        client_impersonated.access_token,
        key=keycloak_public_key,
        options=options,
    )
    assert token_info["preferred_username"] == new_user.username

    delete_user(keycloak_client, new_user)


def test_auth_api_url(client):
    """Test that the auth_api_url property returns the
    correct URL for the default instance of JMS."""
    api = AuthApi(client)
    auth_api_url = client.auth_api_url.rstrip("/")
    assert api.realm_url == f"{auth_api_url}/admin/realms/{client.realm}"
    assert api.url == auth_api_url


def test_customized_auth_api_url(client):
    """Test that the auth_api_url property returns the correct URL for custom entries."""
    # Mock the client object so we can easily force a specific URL that's not the default
    mock_client = MagicMock()
    mock_client.auth_url = "https://example.com/dev/hps/auth/realms/myrealm"

    # Create an instance of AuthApi with the mocked client
    auth_api = AuthApi(client=mock_client)

    # Assert the expected transformation
    assert auth_api.realm_url == "https://example.com/dev/hps/auth/admin/realms/myrealm"
