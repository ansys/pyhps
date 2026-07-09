# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

import pytest

from ansys.hps.client.monitor import MonitorApi
from ansys.hps.client.monitor.api.monitor_api import ClientType

log = logging.getLogger(__name__)


@pytest.fixture
def monitor_api(client):
    return MonitorApi(client, timeout_seconds=10.0)


def test_get_build_info(monitor_api):
    info = monitor_api.get_build_info()
    assert info.build is not None
    assert "version" in info.build or len(info.build) > 0


def test_list_topics(monitor_api):
    topics = monitor_api.list_topics()
    assert isinstance(topics, dict)
    # The monitor should always know about at least one client_type
    assert len(topics) > 0


def test_stream_service_logs_jms(monitor_api):
    messages = list(monitor_api.stream_service_logs(ClientType.JMS, backlog=10, max_messages=10))
    assert isinstance(messages, list)
    for msg in messages:
        assert isinstance(msg, dict)
