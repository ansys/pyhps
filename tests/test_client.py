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

import requests

from ansys.rep.client import Client
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class REPClientTest(REPTestCase):
    def test_client_with_ssl_verification(self):
        with self.assertRaises(requests.exceptions.SSLError) as context:
            _ = Client(self.rep_url, self.username, self.password, verify=True)
        self.assertTrue("CERTIFICATE_VERIFY_FAILED" in str(context.exception))

    def test_authentication_workflows(self):

        ## Auth with user and password
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

        ## Auth with access token
        client1 = Client(self.rep_url, access_token=client0.access_token)
        self.assertEqual(client1.access_token, client0.access_token)
        self.assertTrue(client1.refresh_token is None)

        ## Auth with refresh token
        client2 = Client(
            self.rep_url,
            refresh_token=client0.refresh_token,
            username=client0.username,
        )
        self.assertTrue(client2.access_token is not None)
        self.assertNotEqual(client2.refresh_token, client0.refresh_token)
        client2.refresh_access_token()

        ## Auth with client credentials
        # This is just an example, values are deployment-dependent
        #
        # client3 = Client(
        #     self.rep_url,
        #     client_id="rep-service-account",
        #     client_secret=<your-client-secret>,
        # )
        # self.assertTrue(client3.access_token is not None)
        # self.assertTrue(client3.refresh_token is None)


if __name__ == "__main__":
    unittest.main()
