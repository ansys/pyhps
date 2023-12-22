# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging
import uuid

from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakError

from ansys.hps.client import Client, HPSError
from ansys.hps.client.auth import AuthApi, User, authenticate
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class AuthClientTest(REPTestCase):
    def test_get_users(self):

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
        new_user = self.create_user(new_user)
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

        self.delete_user(new_user)
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

        username = f"test_user_{uuid.uuid4()}"
        new_user = User(
            username=username,
            password="test_auth_client",
            email=f"{username}@test.com",
            first_name="Test",
            last_name="User",
        )
        new_user = self.create_user(new_user)

        realm_clients = self.keycloak_client.get_clients()
        rep_impersonation_client = next(
            (x for x in realm_clients if x["clientId"] == "rep-impersonation"), None
        )
        self.assertTrue(rep_impersonation_client is not None)

        client = Client(
            client_id=rep_impersonation_client["clientId"],
            client_secret=rep_impersonation_client["secret"],
        )

        r = None
        try:
            r = authenticate(
                url=self.rep_url,
                client_id=rep_impersonation_client["clientId"],
                client_secret=rep_impersonation_client["secret"],
                scope="opendid offline_access",
                grant_type="urn:ietf:params:oauth:grant-type:token-exchange",
                subject_token=client.access_token,
                requested_token_type="urn:ietf:params:oauth:token-type:refresh_token",
                requested_subject=new_user.id,
                verify=False,
            )
        except HPSError as e:
            if e.response.status_code == 501 and "Feature not enabled" in e.reason:
                self.skipTest(
                    f"This test requires to enable the feature 'token-exchange' in keycloak."
                )

        self.assertTrue(r is not None)
        self.assertTrue("refresh_token" in r)

        refresh_token_impersonated = r["refresh_token"]

        client_impersonated = Client(
            client.rep_url,
            username=new_user.username,
            grant_type="refresh_token",
            refresh_token=refresh_token_impersonated,
            client_id=rep_impersonation_client["clientId"],
            client_secret=rep_impersonation_client["secret"],
        )

        self.assertTrue(client_impersonated.access_token is not None)
        self.assertTrue(client_impersonated.refresh_token is not None)

        keycloak_openid = KeycloakOpenID(
            server_url=client.auth_api_url,
            client_id="account",
            realm_name="rep",
            client_secret_key="**********",
            verify=False,
        )
        KEYCLOAK_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n"
        KEYCLOAK_PUBLIC_KEY += keycloak_openid.public_key()
        KEYCLOAK_PUBLIC_KEY += "\n-----END PUBLIC KEY-----"

        options = {"verify_signature": True, "verify_aud": True, "verify_exp": True}
        token_info = keycloak_openid.decode_token(
            client_impersonated.access_token,
            key=KEYCLOAK_PUBLIC_KEY,
            options=options,
        )
        self.assertEqual(token_info["preferred_username"], new_user.username)

        self.delete_user(new_user)
