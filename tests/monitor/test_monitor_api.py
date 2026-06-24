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


def _make_ws_mock(monkeypatch, response_payload):
    """Patch websocket.create_connection to return *response_payload* as a single message."""

    class _WebSocketMock:
        def __init__(self):
            self.sent = []
            self._messages = [json.dumps(response_payload)]
            self.closed = False

        def send(self, payload):
            self.sent.append(json.loads(payload))

        def recv(self):
            return self._messages.pop(0) if self._messages else ""

        def close(self):
            self.closed = True

    ws = _WebSocketMock()
    monkeypatch.setitem(
        sys.modules,
        "websocket",
        SimpleNamespace(create_connection=lambda url, timeout: ws),
    )
    return ws


def test_list_topics_sends_list_tags_command(monkeypatch):
    """list_topics sends action=list_tags with the requested limit."""
    server_response = {"tags": {"task_id": ["t1", "t2"], "status": ["RUNNING", "COMPLETED"]}}
    ws = _make_ws_mock(monkeypatch, server_response)

    client = MonitorClient("http://localhost:1089", token="jwt")
    topics = client.list_topics("ws://localhost:1089/dcs/monitor/ws/topics", limit=50)

    sent = ws.sent[0]
    assert sent["type"] == "command"
    assert sent["action"] == "list_tags"
    assert sent["limit"] == 50
    assert sent["token"] == "jwt"
    assert topics == {"task_id": ["t1", "t2"], "status": ["RUNNING", "COMPLETED"]}


def test_list_topics_empty_tags_response(monkeypatch):
    """Server returns empty tags dict."""
    _make_ws_mock(monkeypatch, {"tags": {}})

    client = MonitorClient("http://localhost:1089", token="t")
    topics = client.list_topics("ws://localhost:1089/dcs/monitor/ws/topics")

    assert topics == {}


def test_list_topics_no_response_from_server(monkeypatch):
    """Server sends nothing — list_topics returns empty dict."""

    class _EmptyWsMock:
        def send(self, payload):
            pass

        def recv(self):
            return ""

        def close(self):
            pass

    monkeypatch.setitem(
        sys.modules,
        "websocket",
        SimpleNamespace(create_connection=lambda url, timeout: _EmptyWsMock()),
    )

    client = MonitorClient("http://localhost:1089", token="t")
    topics = client.list_topics("ws://localhost:1089/dcs/monitor/ws/topics")

    assert topics == {}


def test_list_topics_missing_tags_key_in_response(monkeypatch):
    """Server response has no 'tags' key — list_topics returns empty dict."""
    _make_ws_mock(monkeypatch, {"type": "response", "status": "ok"})

    client = MonitorClient("http://localhost:1089", token="t")
    topics = client.list_topics("ws://localhost:1089/dcs/monitor/ws/topics")

    assert topics == {}
