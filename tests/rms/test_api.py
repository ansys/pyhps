import logging
import unittest

from ansys.rep.client.rms import RmsApi
from tests.rep_test import REPTestCase

log = logging.getLogger(__name__)


class RmsApiTest(REPTestCase):
    def test_rms_api_info(self):

        client = self.client
        rms_api = RmsApi(client)

        info = rms_api.get_api_info()
        assert "time" in info
        assert "build" in info


if __name__ == "__main__":
    unittest.main()
