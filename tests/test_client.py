# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging
import time
import unittest

from ansys.rep.client import Client
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class REPClientTest(REPTestCase):
    def test_authentication_workflows(self):

        client0 = Client(self.rep_url, self.username, self.password)

        self.assertTrue(client0.access_token is not None)
        self.assertTrue(client0.refresh_token is not None)

        access_token0 = client0.access_token
        refresh_token0 = client0.refresh_token

        # wait a second otherwise the OAuth server will issue the very same tokens
        time.sleep(1)

        client0.refresh_access_token()
        self.assertNotEqual(client0.access_token, access_token0)
        self.assertNotEqual(client0.refresh_token, refresh_token0)

        client1 = Client(self.rep_url, access_token=client0.access_token)
        self.assertEqual(client1.access_token, client0.access_token)
        self.assertTrue(client1.refresh_token is None)

        client2 = Client(
            self.rep_url,
            refresh_token=client0.refresh_token,
            username=client0.username,
            grant_type="refresh_token",
        )
        self.assertTrue(client2.access_token is not None)
        self.assertNotEqual(client2.refresh_token, client0.refresh_token)
        client2.refresh_access_token()


if __name__ == "__main__":
    unittest.main()
