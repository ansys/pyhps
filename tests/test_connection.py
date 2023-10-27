# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): O.Koenig
# ----------------------------------------------------------
import logging

from ansys.rep.client.auth import authenticate
from ansys.rep.client.connection import create_session, ping
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class ConnectionTest(REPTestCase):
    def test_connection(self):
        rep_url = self.rep_url
        resp = authenticate(
            url=rep_url, username=self.username, password=self.password, verify=False
        )
        access_token = resp["access_token"]

        with create_session(access_token, verify=False, disable_insecure_warnings=True) as session:
            jms_api_url = f"{rep_url}/jms/api/v1"
            log.info(f"Ping {jms_api_url}")
            ping(session, jms_api_url)
            self.assertTrue(ping(session, jms_api_url))
