# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging
import uuid

from ansys.rep.client import Client
from ansys.rep.client.auth import AuthApi, User
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class AuthClientTest(REPTestCase):
    def test_auth_client(self):

        api = AuthApi(Client(self.rep_url, username=self.username, password=self.password))
        users = api.get_users()

        # we run the test only if self.username is an admin user
        for user in users:
            if user.username == self.username and not user.is_admin:
                return

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
