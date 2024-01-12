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

import logging
import time
import unittest

import requests

from ansys.hps.client import Client
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class REPClientTest(REPTestCase):
    def test_client_ssl_warning(self):
        with self.assertWarns(Warning) as context:
            _ = Client(self.rep_url, self.username, self.password)
        log.info(context)
        self.assertTrue("Unverified HTTPS requests" in str(context.warning))

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
