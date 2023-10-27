# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

import requests

from ansys.rep.client.auth import authenticate
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class AuthenticationTest(REPTestCase):
    def test_authenticate(self):
        resp = authenticate(
            url=self.rep_url, username=self.username, password=self.password, verify=False
        )

        self.assertIn("access_token", resp)
        self.assertIn("refresh_token", resp)

    def test_authenticate_with_tls_verification(self):

        with self.assertRaises(requests.exceptions.SSLError) as context:
            _ = authenticate(
                url=self.rep_url, username=self.username, password=self.password, verify=True
            )
        self.assertTrue("CERTIFICATE_VERIFY_FAILED" in str(context.exception))
