# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging
import uuid

from keycloak.exceptions import KeycloakError

from ansys.rep.client import Client, REPError
from ansys.rep.client.auth import AuthApi, User, authenticate
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class AuthClientTest(REPTestCase):
    def test_auth_client(self):

        if not self.is_admin:
            self.skipTest(f"{self.username} is not an admin user.")

        api = AuthApi(self.client)

        username = f"test_user_{uuid.uuid4()}"
        new_user = User(
            username=username,
            password="test_auth_client",
            email=f"{username}@test.com",
            first_name="Test",
            last_name="User",
        )
        new_user = api.create_user(new_user)

        self.assertEqual(new_user.username, username)
        self.assertEqual(new_user.first_name, "Test")
        self.assertEqual(new_user.last_name, "User")
        self.assertEqual(new_user.email, f"{username}@test.com")

        new_user.email = "update_email@test.com"
        new_user.last_name = "Smith"
        api.update_user(new_user)

        self.assertEqual(new_user.username, username)
        self.assertEqual(new_user.first_name, "Test")
        self.assertEqual(new_user.last_name, "Smith")
        self.assertEqual(new_user.email, "update_email@test.com")

        api.delete_user(new_user)

        users = api.get_users()
        usernames = [x.username for x in users]
        self.assertNotIn(new_user.username, usernames)

    def test_get_users(self):

        if not self.is_admin:
            self.skipTest(f"{self.username} is not an admin user.")

        api = AuthApi(self.client)

        # create a new non-admin user
        username = f"test_user_{uuid.uuid4()}"
        new_user = User(
            username=username,
            password="test_auth_client",
            email=f"{username}@test.com",
            first_name="Test",
            last_name="User",
        )
        new_user = api.create_user(new_user)
        self.assertEqual(new_user.first_name, "Test")
        users = api.get_users(max=10)

        # use non-admin user to get users
        api_non_admin = AuthApi(
            Client(self.rep_url, username=username, password="test_auth_client")
        )
        users2 = api_non_admin.get_users(max=10)
        self.assertEqual(len(users), len(users2))

        new_user2 = api.get_user(new_user.id)
        self.assertEqual(new_user, new_user2)

        api.delete_user(new_user)
        users = api.get_users(username=new_user.username)
        self.assertEqual(len(users), 0)

        with self.assertRaises(KeycloakError) as context:
            api.get_user(new_user.id)

        self.assertEqual(context.exception.response_code, 404)

    def test_impersonate_user(self):
        """
        Test token exchange for impersonation, see https://www.rfc-editor.org/rfc/rfc8693.html

        Requires activating the token-exchange feature in keycloak
        by passing --features=token-exchange to the start command.
        """
        if not self.is_admin:
            self.skipTest(f"{self.username} is not an admin user.")

        api = AuthApi(self.client)

        username = f"test_user_{uuid.uuid4()}"
        new_user = User(
            username=username,
            password="test_auth_client",
            email=f"{username}@test.com",
            first_name="Test",
            last_name="User",
        )
        new_user = api.create_user(new_user)

        try:
            r = authenticate(
                url=self.rep_url,
                username=self.username,
                scope="opendid offline_access",
                grant_type="urn:ietf:params:oauth:grant-type:token-exchange",
                subject_token=self.client.access_token,
                requested_token_type="urn:ietf:params:oauth:token-type:refresh_token",
                requested_subject=new_user.id,
            )
        except REPError as e:
            if e.response.status_code == 501 and "Feature not enabled" in e.reason:
                self.skipTest(
                    f"This test requires to enable the feature 'token-exchange' in keycloak."
                )

        refresh_token_impersonated = r["refresh_token"]

        client_impersonated = Client(
            self.rep_url,
            username=new_user.username,
            grant_type="refresh_token",
            refresh_token=refresh_token_impersonated,
        )

        self.assertTrue(client_impersonated.access_token is not None)
        self.assertTrue(client_impersonated.refresh_token is not None)

        api.delete_user(new_user)
