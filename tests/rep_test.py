# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------

import datetime
import logging
import os
import sys
import unittest

from ansys.rep.client.jms import Client


class REPTestCase(unittest.TestCase):

    logger = logging.getLogger("unittestLogger")
    logging.basicConfig(
        format="[%(asctime)s | %(module)8s | %(levelname)6s] %(message)s", level=logging.DEBUG
    )

    def setUp(self):

        # self._stream_handler = logging.StreamHandler(sys.stdout)
        # self.logger.addHandler(self._stream_handler)

        self.rep_url = os.environ.get("REP_TEST_URL") or "https://127.0.0.1:8443/rep"
        self.username = os.environ.get("REP_TEST_USERNAME") or "repadmin"
        self.password = os.environ.get("REP_TEST_PASSWORD") or "repadmin"

        # Create a unique run_id (to be used when creating new projects) to avoid conflicts in case of
        # multiple builds testing against the same REP server.
        # If tests are run on TFS we create this run_id combining the Agent.Id and Build.BuildId env variables.
        agent_id = os.environ.get("Agent.Id")
        if agent_id is None:
            if os.name == "nt":
                agent_id = os.environ.get("COMPUTERNAME", "localhost")
            else:
                agent_id = os.environ.get("HOSTNAME", "localhost")

        build_id = os.environ.get("Build.BuildId", "1")
        self.run_id = f"{agent_id}_{build_id}".lower()

    def tearDown(self):
        # self.logger.removeHandler(self._stream_handler)
        pass

    def jms_client(self):
        return Client(self.rep_url, self.username, self.password)
