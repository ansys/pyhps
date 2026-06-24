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

import json
import sys
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit

import pytest

from ansys.hps.client.monitor import MonitorClient, build_filter_templates


class _ResponseMock:
    def __init__(self, payload):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


def test_get_build_info_uses_expected_endpoint_and_auth_header(monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["method"] = req.get_method()
        captured["headers"] = dict(req.header_items())
        captured["timeout"] = timeout
        return _ResponseMock({"build": {"version": "1.2.3"}})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = MonitorClient("http://localhost:1089/", token="jwt-token", timeout_seconds=3.5)
    response = client.get_build_info()

    assert response["build"]["version"] == "1.2.3"
    assert captured["url"] == "http://localhost:1089/dcs/monitor/api/"
    assert captured["method"] == "GET"
    assert captured["headers"]["Authorization"] == "Bearer jwt-token"
    assert captured["timeout"] == 3.5


def test_query_logs_serializes_filters(monkeypatch):
    captured = {}

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["method"] = req.get_method()
        captured["headers"] = dict(req.header_items())
        captured["timeout"] = timeout
        return _ResponseMock({"messages": []})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = MonitorClient("http://localhost:1089", token="abc", timeout_seconds=5.0)
    response = client.query_logs(
        {
            "tag:host": ["h1", "h2"],
            "severity": "info",
            "limit": 5,
        }
    )

    parsed = urlsplit(captured["url"])
    query_params = parse_qs(parsed.query)

    assert response == {"messages": []}
    assert parsed.path == "/dcs/monitor/api/log"
    assert query_params["tag:host"] == ["h1,h2"]
    assert query_params["severity"] == ["info"]
    assert query_params["limit"] == ["5"]
    assert captured["method"] == "GET"
    assert captured["headers"]["Authorization"] == "Bearer abc"
    assert captured["timeout"] == 5.0


def test_send_ws_command_adds_token_and_collects_messages(monkeypatch):
    captured = {"ws_url": None, "timeout": None}

    class _WebSocketMock:
        def __init__(self):
            self.sent = []
            self._recv_messages = [json.dumps({"id": 1}), json.dumps({"id": 2}), ""]
            self.closed = False

        def send(self, payload):
            self.sent.append(payload)

        def recv(self):
            return self._recv_messages.pop(0)

        def close(self):
            self.closed = True

    ws = _WebSocketMock()

    def fake_create_connection(ws_url, timeout):
        captured["ws_url"] = ws_url
        captured["timeout"] = timeout
        return ws

    monkeypatch.setitem(sys.modules, "websocket", SimpleNamespace(create_connection=fake_create_connection))

    client = MonitorClient("http://localhost:1089", token="jwt", timeout_seconds=7.0)
    responses = client.send_ws_command(
        "ws://localhost:1089/dcs/monitor/ws/topics",
        {"type": "command", "action": "subscribe"},
        max_messages=5,
    )

    sent_command = json.loads(ws.sent[0])
    assert captured["ws_url"] == "ws://localhost:1089/dcs/monitor/ws/topics"
    assert captured["timeout"] == 7.0
    assert sent_command["token"] == "jwt"
    assert responses == [{"id": 1}, {"id": 2}]
    assert ws.closed is True


def test_send_ws_command_preserves_existing_token(monkeypatch):
    class _WebSocketMock:
        def __init__(self):
            self.sent = []

        def send(self, payload):
            self.sent.append(payload)

        def recv(self):
            return ""

        def close(self):
            return None

    ws = _WebSocketMock()

    def fake_create_connection(ws_url, timeout):
        return ws

    monkeypatch.setitem(sys.modules, "websocket", SimpleNamespace(create_connection=fake_create_connection))

    client = MonitorClient("http://localhost:1089", token="jwt")
    client.send_ws_command(
        "ws://localhost:1089/dcs/monitor/ws/topics",
        {"type": "command", "token": "already-present"},
    )

    sent_command = json.loads(ws.sent[0])
    assert sent_command["token"] == "already-present"


def test_send_ws_command_raises_helpful_error_without_websocket_client(monkeypatch):
    monkeypatch.delitem(sys.modules, "websocket", raising=False)

    real_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "websocket":
            raise ImportError("missing websocket-client")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)

    client = MonitorClient("http://localhost:1089")
    with pytest.raises(RuntimeError, match="websocket-client is required"):
        client.send_ws_command("ws://localhost:1089/dcs/monitor/ws/topics", {"type": "command"})


def test_build_filter_templates_returns_expected_structure():
    templates = build_filter_templates(["host", "service"])

    assert templates["rest"]["path"] == "/dcs/monitor/api/log"
    assert templates["rest"]["query_params"] == {
        "tag:host": ["value"],
        "tag:service": ["value"],
    }
    assert templates["websocket"]["path"] == "/dcs/monitor/ws/topics"
    assert templates["websocket"]["command"]["action"] == "subscribe"
    assert templates["websocket"]["command"]["topics"] == [{"host": "value", "service": "value"}]
    assert templates["websocket"]["command"]["backlog"] == {"limit": 100}


# ---------------------------------------------------------------------------
# list_topics tests
# ---------------------------------------------------------------------------


def _make_urlopen_mock(monkeypatch, payload):
    """Patch urllib.request.urlopen to return *payload* as JSON."""

    def fake_urlopen(req, timeout):
        return _ResponseMock(payload)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)


def test_list_topics_with_nested_tags_dict(monkeypatch):
    """Response is a list of entries each with a nested 'tags' dict."""
    entries = [
        {"message": "a", "tags": {"task_id": "task-1", "status": "RUNNING"}},
        {"message": "b", "tags": {"task_id": "task-2", "status": "COMPLETED"}},
        {"message": "c", "tags": {"task_id": "task-1", "status": "COMPLETED"}},
    ]
    _make_urlopen_mock(monkeypatch, entries)

    client = MonitorClient("http://localhost:1089", token="t")
    topics = client.list_topics()

    assert topics["task_id"] == {"task-1", "task-2"}
    assert topics["status"] == {"RUNNING", "COMPLETED"}


def test_list_topics_with_flat_tag_prefix_keys(monkeypatch):
    """Response is a list of entries with flat 'tag:<key>' top-level fields."""
    entries = [
        {"tag:job_id": "job-A", "tag:host": "host-1"},
        {"tag:job_id": "job-B", "tag:host": "host-2"},
        {"tag:job_id": "job-A", "tag:host": "host-1"},
    ]
    _make_urlopen_mock(monkeypatch, entries)

    client = MonitorClient("http://localhost:1089", token="t")
    topics = client.list_topics()

    assert topics["job_id"] == {"job-A", "job-B"}
    assert topics["host"] == {"host-1", "host-2"}


def test_list_topics_with_dict_envelope(monkeypatch):
    """Response is a dict with entries nested under a known key (e.g. 'logs')."""
    payload = {
        "logs": [
            {"tags": {"task_id": "task-X"}},
            {"tags": {"task_id": "task-Y"}},
        ]
    }
    _make_urlopen_mock(monkeypatch, payload)

    client = MonitorClient("http://localhost:1089", token="t")
    topics = client.list_topics()

    assert topics["task_id"] == {"task-X", "task-Y"}


def test_list_topics_empty_response(monkeypatch):
    """Empty log response returns empty topics dict."""
    _make_urlopen_mock(monkeypatch, [])

    client = MonitorClient("http://localhost:1089", token="t")
    topics = client.list_topics()

    assert topics == {}


def test_list_topics_passes_limit_to_query(monkeypatch):
    """list_topics forwards the limit parameter to query_logs."""
    captured = {}

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        return _ResponseMock([])

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = MonitorClient("http://localhost:1089", token="t")
    client.list_topics(limit=42)

    parsed = urlsplit(captured["url"])
    assert parse_qs(parsed.query).get("limit") == ["42"]
