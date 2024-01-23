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

from ansys.hps.core.auth import authenticate
from ansys.hps.core.connection import create_session, ping
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class ConnectionTest(REPTestCase):
    def test_connection(self):
        rep_url = self.rep_url
        resp = authenticate(
            url=rep_url, username=self.username, password=self.password, verify=False
        )
        access_token = resp["access_token"]

        with create_session(access_token, verify=False, disable_security_warnings=True) as session:
            jms_api_url = f"{rep_url}/jms/api/v1"
            log.info(f"Ping {jms_api_url}")
            ping(session, jms_api_url)
            self.assertTrue(ping(session, jms_api_url))
