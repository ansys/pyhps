# ----------------------------------------------------------
# Copyright (C) 2019 by
# ANSYS Switzerland GmbH
# www.ansys.com
#
# Author(s): F.Negri
# ----------------------------------------------------------

import logging
import os
import unittest

from ansys.rep.client import Client


class REPTestCase(unittest.TestCase):

    logger = logging.getLogger("unittestLogger")
    logging.basicConfig(
        format="[%(asctime)s | %(module)8s | %(levelname)6s] %(message)s", level=logging.DEBUG
    )

    def setUp(self):

        # self._stream_handler = logging.StreamHandler(sys.stdout)
        # self.logger.addHandler(self._stream_handler)

        self.rep_url = os.environ.get("REP_TEST_URL") or "https://repkube-dev.westeurope.cloudapp.azure.com/rep"
        self.username = os.environ.get("REP_TEST_USERNAME") or "repadmin"
        self.password = os.environ.get("REP_TEST_PASSWORD") or "repadmin"

        # Create a unique run_id (to be used when creating new projects)
        # to avoid conflicts in case of
        # multiple builds testing against the same REP server.
        # If tests are run on TFS we create this run_id combining the Agent.Id
        # and Build.BuildId env variables.
        agent_id = os.environ.get("Agent.Id")
        if agent_id is None:
            if os.name == "nt":
                agent_id = os.environ.get("COMPUTERNAME", "localhost")
            else:
                agent_id = os.environ.get("HOSTNAME", "localhost")

        build_id = os.environ.get("Build.BuildId", "1")
        self.run_id = f"{agent_id}_{build_id}".lower()

        self._client = None

    def tearDown(self):
        # self.logger.removeHandler(self._stream_handler)
        pass

    def client(self):
        if self._client is None:
            self._client = Client(self.rep_url, self.username, self.password)
        return self._client
