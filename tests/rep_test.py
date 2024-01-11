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

# ----------------------------------------------------------
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------

import logging
import os
from typing import Tuple
import unittest
import uuid

from keycloak import KeycloakAdmin

from ansys.hps.client import Client
from ansys.hps.client.auth import AuthApi, User
from ansys.hps.client.auth.api.auth_api import create_user


class REPTestCase(unittest.TestCase):

    logger = logging.getLogger("unittestLogger")
    logging.basicConfig(
        format="[%(asctime)s | %(module)8s | %(levelname)6s] %(message)s", level=logging.DEBUG
    )

    def setUp(self):

        # self._stream_handler = logging.StreamHandler(sys.stdout)
        # self.logger.addHandler(self._stream_handler)

        self.rep_url = os.environ.get("REP_TEST_URL") or "https://127.0.0.1:8443/rep"
        self.username = os.environ.get("REP_TEST_USERNAME") or "repadmin"
        self.password = os.environ.get("REP_TEST_PASSWORD") or "repadmin"
        self.keycloak_username = os.environ.get("REP_TEST_KEYCLOAK_USERNAME") or "keycloak"
        self.keycloak_password = os.environ.get("REP_TEST_KEYCLOAK_PASSWORD") or "keycloak123"

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
        self.run_id = f"{agent_id}_{build_id}".lower()

        self._client = None
        self._keycloak_client = None
        self._is_admin = None

    def tearDown(self):
        # self.logger.removeHandler(self._stream_handler)
        pass

    @property
    def client(self) -> Client:
        if self._client is None:
            self._client = Client(self.rep_url, self.username, self.password, verify=False)
        return self._client

    @property
    def keycloak_client(self) -> KeycloakAdmin:
        if self._keycloak_client is None:
            self._keycloak_client = KeycloakAdmin(
                server_url=self.client.auth_api_url,
                username=self.keycloak_username,
                password=self.keycloak_password,
                realm_name="master",
                client_id="admin-cli",
                verify=False,
            )
            self._keycloak_client.realm_name = "rep"
        return self._keycloak_client

    @property
    def is_admin(self):
        if self._is_admin is None:
            api = AuthApi(self.client)
            users = api.get_users(username=self.username)
            self.assertEqual(len(users), 1)
            self._is_admin = api.user_is_admin(users[0].id)
        return self._is_admin

    def create_user(self, user: User) -> User:
        return create_user(self.keycloak_client, user)

    def delete_user(self, user: User) -> User:
        return self.keycloak_client.delete_user(user.id)

    def create_new_user_client(
        self,
        username=None,
        password="test",
    ) -> Tuple[User, Client]:

        if username is None:
            username = f"testuser-{uuid.uuid4().hex[:8]}"

        user = self.create_user(User(username=username, password=password))
        client = Client(
            rep_url=self.rep_url,
            username=user.username,
            password=password,
        )
        return user, client
