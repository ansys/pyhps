# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

from ansys.rep.client.auth import Client, User
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class AuthClientTest(REPTestCase):
    def test_auth_client(self):

        cl = Client(self.rep_url, username=self.username, password=self.password)
        users = cl.get_users()

        # we run the test only if self.username is an admin user
        for user in users:
            if user.username == self.username and not user.is_admin:
                return

        username = f"test_user_{self.run_id}"
        new_user = User(
            username=username,
            password="test_auth_client",
            email="test_auth_client@test.com",
            first_name="Test",
            last_name="User",
        )
        new_user = cl.create_user(new_user)

        self.assertEqual(new_user.username, username)
        self.assertEqual(new_user.first_name, "Test")
        self.assertEqual(new_user.last_name, "User")
        self.assertEqual(new_user.email, "test_auth_client@test.com")

        new_user.email = "update_email@test.com"
        new_user.last_name = "Smith"
        cl.update_user(new_user)

        self.assertEqual(new_user.username, username)
        self.assertEqual(new_user.first_name, "Test")
        self.assertEqual(new_user.last_name, "Smith")
        self.assertEqual(new_user.email, "update_email@test.com")

        cl.delete_user(new_user)

        users = cl.get_users()
        usernames = [x.username for x in users]
        self.assertNotIn(new_user.username, usernames)
