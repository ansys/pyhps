# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------
import logging
import unittest

from ansys.rep.client import APIError, Client, ClientError
from ansys.rep.client.jms import JmsApi
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class ExceptionTest(REPTestCase):
    def test_server_error(self):

        client = self.client()
        jms_api = JmsApi(client)
        except_obj = None
        try:
            jms_api.get_projects(wrong_query_param="value")
        except APIError as e:
            except_obj = e
            log.error(str(e))

        self.assertEqual(except_obj.reason, "500 Internal Server Error")
        self.assertEqual(
            except_obj.description, "type object 'Project' has no attribute 'wrong_query_param'"
        )
        self.assertEqual(except_obj.response.status_code, 500)

    def test_client_error(self):

        except_obj = None
        try:
            client = Client(self.rep_url, self.username, f"{self.password}_wrong")
        except ClientError as e:
            except_obj = e
            log.error(str(e))

        self.assertEqual(except_obj.reason, "invalid_grant")
        self.assertEqual(except_obj.description, "Invalid user credentials")
        self.assertEqual(except_obj.response.status_code, 401)

        except_obj = None
        try:
            client = self.client()
            jms_api = JmsApi(client)
            jms_api.get_project(id="02q4bg9PVO2OvvhsmClb0E")
        except ClientError as e:
            except_obj = e
            log.error(str(e))

        # The answer that one would expect:
        # self.assertEqual(except_obj.reason, 'Not Found')
        # self.assertEqual(except_obj.response.status_code, 404)
        # The answer currently received when querying this with a user different from repadmin
        self.assertEqual(except_obj.reason, "404 Not Found")
        self.assertEqual(except_obj.response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
