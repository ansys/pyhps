# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging
import unittest

from ansys.rep.client.auth import authenticate
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class AuthenticationTest(REPTestCase):
    def test_authenticate(self):

        if self.pat:
            raise unittest.SkipTest("This test is not supported with PAT authentication.")

        resp = authenticate(url=self.rep_url, username=self.username, password=self.password)

        self.assertIn("access_token", resp)
        self.assertIn("refresh_token", resp)
