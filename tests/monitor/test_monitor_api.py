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
    captured = {"ws_url": None, "timeout": None, "header": None}

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

    def fake_create_connection(ws_url, **kwargs):
        captured["ws_url"] = ws_url
        captured["timeout"] = kwargs.get("timeout")
        captured["header"] = kwargs.get("header")
        return ws

    monkeypatch.setitem(sys.modules, "websocket", SimpleNamespace(create_connection=fake_create_connection))

    client = MonitorClient("http://localhost:1089", token="jwt", timeout_seconds=7.0)
    responses = client.send_ws_command(
        "ws://localhost:1089/monitor/ws/topics",
        {"type": "command", "action": "subscribe"},
        max_messages=5,
    )

    sent_command = json.loads(ws.sent[0])
    assert captured["ws_url"] == "ws://localhost:1089/monitor/ws/topics"
    assert captured["timeout"] == 7.0
    assert captured["header"] == {"Authorization": "Bearer jwt"}
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

    def fake_create_connection(ws_url, **kwargs):
        return ws

    monkeypatch.setitem(sys.modules, "websocket", SimpleNamespace(create_connection=fake_create_connection))

    client = MonitorClient("http://localhost:1089", token="jwt")
    client.send_ws_command(
        "ws://localhost:1089/monitor/ws/topics",
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
        client.send_ws_command("ws://localhost:1089/monitor/ws/topics", {"type": "command"})


def test_integration_client_uses_provided_client_without_token():
    provided = SimpleNamespace(name="provided-client")
    client = MonitorClient("http://localhost:1089", client=provided)

    resolved = client._integration_client()

    assert resolved is provided


def test_send_ws_command_without_token_sends_no_auth_header(monkeypatch):
    captured = {"header": "not-set"}

    class _WebSocketMock:
        def send(self, payload):
            pass

        def recv(self):
            return ""

        def close(self):
            return None

    def fake_create_connection(ws_url, **kwargs):
        captured["header"] = kwargs.get("header")
        return _WebSocketMock()

    monkeypatch.setitem(sys.modules, "websocket", SimpleNamespace(create_connection=fake_create_connection))

    client = MonitorClient("http://localhost:1089")
    client.send_ws_command("ws://localhost:1089/monitor/ws/topics", {"type": "command"})

    assert captured["header"] is None


def test_send_ws_command_forwards_ws_connection_options_and_merges_auth_header(monkeypatch):
    captured = {"timeout": None, "header": None, "sslopt": None}

    class _WebSocketMock:
        def send(self, payload):
            pass

        def recv(self):
            return ""

        def close(self):
            return None

    def fake_create_connection(ws_url, **kwargs):
        captured["timeout"] = kwargs.get("timeout")
        captured["header"] = kwargs.get("header")
        captured["sslopt"] = kwargs.get("sslopt")
        return _WebSocketMock()

    monkeypatch.setitem(sys.modules, "websocket", SimpleNamespace(create_connection=fake_create_connection))

    client = MonitorClient(
        "http://localhost:1089",
        token="jwt",
        timeout_seconds=7.5,
        ws_connection_options={
            "sslopt": {"cert_reqs": 0},
            "header": {"X-Test": "ok"},
        },
    )
    client.send_ws_command("ws://localhost:1089/monitor/ws/topics", {"type": "command"})

    assert captured["timeout"] == 7.5
    assert captured["sslopt"] == {"cert_reqs": 0}
    assert captured["header"]["X-Test"] == "ok"
    assert captured["header"]["Authorization"] == "Bearer jwt"


def test_build_filter_templates_returns_expected_structure():
    templates = build_filter_templates(["host", "service"])

    assert templates["rest"]["path"] == "/dcs/monitor/api/log"
    assert templates["rest"]["query_params"] == {
        "tag:host": ["value"],
        "tag:service": ["value"],
    }
    assert templates["websocket"]["path"] == "/monitor/ws/topics"
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
        SimpleNamespace(create_connection=lambda url, **kwargs: ws),
    )
    return ws


def test_list_topics_sends_list_tags_command(monkeypatch):
    """list_topics sends action=list_tags with the requested limit."""
    server_response = {"tags": {"task_id": ["t1", "t2"], "status": ["RUNNING", "COMPLETED"]}}
    ws = _make_ws_mock(monkeypatch, server_response)

    client = MonitorClient("http://localhost:1089", token="jwt")
    topics = client.list_topics("ws://localhost:1089/monitor/ws/topics", limit=50)

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
    topics = client.list_topics("ws://localhost:1089/monitor/ws/topics")

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
        SimpleNamespace(create_connection=lambda url, **kwargs: _EmptyWsMock()),
    )

    client = MonitorClient("http://localhost:1089", token="t")
    topics = client.list_topics("ws://localhost:1089/monitor/ws/topics")

    assert topics == {}


def test_list_topics_missing_tags_key_in_response(monkeypatch):
    """Server response has no 'tags' key — list_topics returns empty dict."""
    _make_ws_mock(monkeypatch, {"type": "response", "status": "ok"})

    client = MonitorClient("http://localhost:1089", token="t")
    topics = client.list_topics("ws://localhost:1089/monitor/ws/topics")

    assert topics == {}


def test_list_topics_uses_derived_ws_url_when_omitted(monkeypatch):
    """list_topics derives ws_url from base_url when ws_url is not provided."""
    captured = {}

    class _WsMock:
        def __init__(self, url):
            captured["url"] = url

        def send(self, payload):
            pass

        def recv(self):
            return json.dumps({"tags": {}})

        def close(self):
            pass

    monkeypatch.setitem(
        sys.modules,
        "websocket",
        SimpleNamespace(create_connection=lambda url, **kwargs: _WsMock(url)),
    )

    client = MonitorClient("https://localhost:8443/hps", token="t")
    topics = client.list_topics(limit=25)

    assert topics == {}
    assert captured["url"] == "wss://localhost:8443/hps/monitor/ws/topics"


# ---------------------------------------------------------------------------
# stream_task_host_resources tests
# ---------------------------------------------------------------------------


def _make_multi_ws_mock(monkeypatch, messages):
    """Patch websocket.create_connection to return multiple messages sequentially."""

    class _MultiWsMock:
        def __init__(self):
            self.sent = []
            self._messages = [json.dumps(m) for m in messages]
            self.closed = False

        def send(self, payload):
            self.sent.append(json.loads(payload))

        def recv(self):
            return self._messages.pop(0) if self._messages else ""

        def close(self):
            self.closed = True

    ws = _MultiWsMock()
    monkeypatch.setitem(
        sys.modules,
        "websocket",
        SimpleNamespace(create_connection=lambda url, **kwargs: ws),
    )
    return ws


def test_stream_task_host_resources_sends_correct_topic(monkeypatch):
    """stream_task_host_resources subscribes with the correct topic tags."""
    ws = _make_multi_ws_mock(monkeypatch, [{"cpu_percent": 42.0, "memory_percent": 55.1}])

    client = MonitorClient("http://localhost:1089", token="jwt")
    monkeypatch.setattr(client, "_resolve_evaluator_name_for_task", lambda task_id: "eval-1")
    results = list(client.stream_task_host_resources("task-abc"))

    sent = ws.sent[0]
    assert sent["type"] == "command"
    assert sent["action"] == "subscribe"
    assert sent["token"] == "jwt"
    topic = sent["topics"][0]
    assert topic["evaluator_name"] == "eval-1"
    assert topic["client_type"] == "ansys.rep.evaluator"
    assert topic["type"] == "metric"
    assert topic["statistic"] == "host_resources"


def test_stream_task_host_resources_yields_messages(monkeypatch):
    """stream_task_host_resources yields each metric update as it arrives."""
    updates = [
        {"cpu_percent": 10.0, "memory_percent": 30.0},
        {"cpu_percent": 20.0, "memory_percent": 35.0},
        {"cpu_percent": 15.0, "memory_percent": 32.0},
    ]
    _make_multi_ws_mock(monkeypatch, updates)

    client = MonitorClient("http://localhost:1089", token="t")
    monkeypatch.setattr(client, "_resolve_evaluator_name_for_task", lambda task_id: "eval-1")
    results = list(client.stream_task_host_resources("task-abc", max_messages=10))

    assert results == updates


def test_stream_task_host_resources_unwraps_messages_envelope(monkeypatch):
    envelopes = [{"messages": [{"cpu_percent": 10.0}, {"cpu_percent": 20.0}]}]
    _make_multi_ws_mock(monkeypatch, envelopes)

    client = MonitorClient("http://localhost:1089", token="t")
    monkeypatch.setattr(client, "_resolve_evaluator_name_for_task", lambda task_id: "eval-1")
    results = list(client.stream_task_host_resources("task-abc", max_messages=10))

    assert results == [{"cpu_percent": 10.0}, {"cpu_percent": 20.0}]


def test_stream_task_host_resources_stops_cleanly_on_websocket_timeout(monkeypatch):
    class WebSocketTimeoutException(Exception):
        pass

    class _TimeoutWsMock:
        def __init__(self):
            self.sent = []

        def send(self, payload):
            self.sent.append(json.loads(payload))

        def recv(self):
            raise WebSocketTimeoutException("Connection timed out")

        def close(self):
            return None

    monkeypatch.setitem(
        sys.modules,
        "websocket",
        SimpleNamespace(create_connection=lambda url, **kwargs: _TimeoutWsMock()),
    )

    client = MonitorClient("http://localhost:1089", token="t")
    monkeypatch.setattr(client, "_resolve_evaluator_name_for_task", lambda task_id: "eval-1")
    results = list(client.stream_task_host_resources("task-abc", max_messages=10))

    assert results == []


def test_stream_task_host_resources_respects_backlog(monkeypatch):
    """backlog parameter is forwarded in the subscribe command."""
    ws = _make_multi_ws_mock(monkeypatch, [])

    client = MonitorClient("http://localhost:1089", token="t")
    monkeypatch.setattr(client, "_resolve_evaluator_name_for_task", lambda task_id: "eval-1")
    list(client.stream_task_host_resources("task-abc", backlog=42))

    assert ws.sent[0]["backlog"] == {"limit": 42}


def test_stream_task_host_resources_respects_max_messages(monkeypatch):
    """max_messages caps the number of yielded updates."""
    updates = [{"cpu_percent": float(i)} for i in range(10)]
    _make_multi_ws_mock(monkeypatch, updates)

    client = MonitorClient("http://localhost:1089", token="t")
    monkeypatch.setattr(client, "_resolve_evaluator_name_for_task", lambda task_id: "eval-1")
    results = list(client.stream_task_host_resources("task-abc", max_messages=3))

    assert len(results) == 3


def test_stream_task_host_resources_uses_derived_ws_url(monkeypatch):
    """ws_url is derived from base_url when not explicitly provided."""
    captured = {}

    class _WsMock:
        def __init__(self, url):
            captured["url"] = url

        def send(self, payload):
            pass

        def recv(self):
            return ""

        def close(self):
            pass

    monkeypatch.setitem(
        sys.modules,
        "websocket",
        SimpleNamespace(create_connection=lambda url, **kwargs: _WsMock(url)),
    )

    client = MonitorClient("https://localhost:8443/hps", token="t")
    monkeypatch.setattr(client, "_resolve_evaluator_name_for_task", lambda task_id: "eval-1")
    list(client.stream_task_host_resources("task-abc"))

    assert captured["url"] == "wss://localhost:8443/hps/monitor/ws/topics"


def test_stream_task_host_resources_raises_when_evaluator_resolution_fails(monkeypatch):
    _make_multi_ws_mock(monkeypatch, [])

    client = MonitorClient("http://localhost:1089", token="t")
    monkeypatch.setattr(
        client,
        "_resolve_evaluator_name_for_task",
        lambda task_id: (_ for _ in ()).throw(RuntimeError("not found")),
    )

    with pytest.raises(RuntimeError, match="not found"):
        list(client.stream_task_host_resources("task-abc"))


def test_stream_task_logs_unlimited_when_max_messages_none(monkeypatch):
    """max_messages=None should stream until server closes connection."""
    updates = [{"message": "a"}, {"message": "b"}, {"message": "c"}]
    _make_multi_ws_mock(monkeypatch, updates)

    client = MonitorClient("http://localhost:1089", token="t")
    results = list(client.stream_task_logs("task-abc", max_messages=None))

    assert results == updates
