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
# SOFTWARE.


import os

from keycloak import KeycloakAdmin
import pytest

from ansys.hps.client import AuthApi, Client


@pytest.fixture(scope="session")
def url():
    return os.environ.get("HPS_TEST_URL") or "https://127.0.0.1:8443/rep"


@pytest.fixture(scope="session")
def username():
    return os.environ.get("HPS_TEST_USERNAME") or "repadmin"


@pytest.fixture(scope="session")
def password():
    return os.environ.get("HPS_TEST_PASSWORD") or "repadmin"


@pytest.fixture(scope="session")
def keycloak_username():
    return os.environ.get("HPS_TEST_KEYCLOAK_USERNAME") or "keycloak"


@pytest.fixture(scope="session")
def keycloak_password():
    return os.environ.get("HPS_TEST_KEYCLOAK_PASSWORD") or "keycloak123"


@pytest.fixture(scope="session")
def client(url, username, password):
    return Client(url, username, password, verify=False)


@pytest.fixture()
def keycloak_client(client: Client, keycloak_username, keycloak_password):

    keycloak_client = KeycloakAdmin(
        server_url=client.auth_api_url,
        username=keycloak_username,
        password=keycloak_password,
        realm_name="rep",
        user_realm_name="master",
        client_id="admin-cli",
        verify=False,
    )

    return keycloak_client


@pytest.fixture(scope="session")
def is_admin(client: Client):
    api = AuthApi(client)
    users = api.get_users(username=client.username)
    assert len(users) == 1
    return api.user_is_admin(users[0].id)


@pytest.fixture()
def run_id():
    # Create a unique run_id (to be used when creating new projects)
    # to avoid conflicts in case of
    # multiple builds testing against the same REP server.
    # If tests are run on TFS we create this run_id combining the Agent.Id
    # and Build.BuildId env variables.
    agent_id = os.environ.get("Agent.Id")
    if agent_id is None:
        if os.name == "nt":
            agent_id = os.environ.get("COMPUTERNAME", "localhost")
        else:
            agent_id = os.environ.get("HOSTNAME", "localhost")
    build_id = os.environ.get("Build.BuildId", "1")
    return f"{agent_id}_{build_id}".lower()
