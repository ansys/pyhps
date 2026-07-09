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

import importlib
import json
import sys
from types import SimpleNamespace
from typing import Any
from urllib.parse import parse_qs, urlsplit

import pytest

import ansys.hps.client.monitor.api.monitor_api as monitor_api_module
from ansys.hps.client import ClientError
from ansys.hps.client.monitor import MonitorApi, build_filter_templates

BASE_URL = "http://localhost:1089"
BASE_URL_HTTPS = "https://localhost:8443/hps"
WS_TOPICS_URL = "ws://localhost:1089/monitor/ws/topics"
WSS_TOPICS_URL = "wss://localhost:8443/hps/monitor/ws/topics"


def _make_hps_client(
    url: str = BASE_URL,
    access_token: str | None = None,
    session: Any | None = None,
):
    if session is None:
        session = SimpleNamespace(get=lambda *args, **kwargs: None)
    return SimpleNamespace(url=url, access_token=access_token, session=session)


class _ResponseMock:
    def __init__(self, payload):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


def test_monitor_api_module_reload_executes_definitions():
    reloaded = importlib.reload(monitor_api_module)

    assert reloaded.ClientType.FILE_TAIL == "ansys.rep.evaluator.file_tail"
    assert hasattr(reloaded, "MonitorApi")


def test_get_build_info_uses_expected_endpoint_and_auth_header(monkeypatch):
    captured = {}

    class _RequestsResponseMock:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    class _SessionMock:
        def get(self, url, timeout):
            captured["url"] = url
            captured["timeout"] = timeout
            return _RequestsResponseMock({"build": {"version": "1.2.3"}})

    hps_client = _make_hps_client(
        url=f"{BASE_URL}/",
        access_token="jwt-token",
        session=_SessionMock(),
    )

    client = MonitorApi(hps_client, timeout_seconds=3.5)
    response = client.get_build_info()

    assert response["build"]["version"] == "1.2.3"
    assert captured["url"] == f"{BASE_URL}/dcs/monitor/api/"
    assert captured["timeout"] == 3.5


def test_query_logs_serializes_filters(monkeypatch):
    captured = {}

    class _RequestsResponseMock:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    class _SessionMock:
        def get(self, url, timeout):
            captured["url"] = url
            captured["timeout"] = timeout
            return _RequestsResponseMock({"messages": []})

    hps_client = _make_hps_client(
        url=BASE_URL,
        access_token="abc",
        session=_SessionMock(),
    )

    client = MonitorApi(hps_client, timeout_seconds=5.0)
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

    monkeypatch.setitem(
        sys.modules, "websocket", SimpleNamespace(create_connection=fake_create_connection)
    )

    client = MonitorApi(_make_hps_client(access_token="jwt"), timeout_seconds=7.0)
    responses = client.send_ws_command(
        {"type": "command", "action": "subscribe"},
        max_messages=5,
    )

    sent_command = json.loads(ws.sent[0])
    assert captured["ws_url"] == WS_TOPICS_URL
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

    monkeypatch.setitem(
        sys.modules, "websocket", SimpleNamespace(create_connection=fake_create_connection)
    )

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="jwt"))
    client.send_ws_command(
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

    client = MonitorApi(_make_hps_client(url=BASE_URL))
    with pytest.raises(ClientError, match="websocket-client is required"):
        client.send_ws_command({"type": "command"})


def test_integration_client_uses_provided_client_without_token():
    provided = SimpleNamespace(name="provided-client")
    client = MonitorApi(provided)

    resolved = client._integration_client()

    assert resolved is provided


def test_auth_headers_without_token_returns_empty_dict():
    client = MonitorApi(_make_hps_client(url=BASE_URL))

    assert client._auth_headers() == {}


def test_resolve_evaluator_name_for_task_success(monkeypatch):
    provided = SimpleNamespace(name="provided-client")
    captured = {"project_id": None, "task_id": None, "host_id": None}

    class _ProjectApiMock:
        def __init__(self, client, project_id):
            captured["project_id"] = project_id

        def get_tasks(self, id, fields):
            captured["task_id"] = id
            assert fields == ["id", "host_id"]
            return [SimpleNamespace(host_id="host-1")]

    class _RmsApiMock:
        def __init__(self, client):
            pass

        def get_evaluators(self, host_id, fields):
            captured["host_id"] = host_id
            assert fields == ["id", "name", "host_id"]
            return [SimpleNamespace(name="eval-1")]

    monkeypatch.setattr("ansys.hps.client.jms.ProjectApi", _ProjectApiMock)
    monkeypatch.setattr("ansys.hps.client.rms.RmsApi", _RmsApiMock)

    client = MonitorApi(provided)
    evaluator_name = client._resolve_evaluator_name_for_task("task-abc", "proj-123")

    assert evaluator_name == "eval-1"
    assert captured["project_id"] == "proj-123"
    assert captured["task_id"] == "task-abc"
    assert captured["host_id"] == "host-1"


def test_resolve_evaluator_name_for_task_raises_when_task_not_found(monkeypatch):
    class _ProjectApiMock:
        def __init__(self, client, project_id):
            pass

        def get_tasks(self, id, fields):
            return []

    monkeypatch.setattr("ansys.hps.client.jms.ProjectApi", _ProjectApiMock)

    client = MonitorApi(_make_hps_client(url=BASE_URL))
    with pytest.raises(ClientError, match="Could not resolve host_id"):
        client._resolve_evaluator_name_for_task("task-abc", "proj-123")


def test_resolve_evaluator_name_for_task_raises_when_no_evaluator(monkeypatch):
    class _ProjectApiMock:
        def __init__(self, client, project_id):
            pass

        def get_tasks(self, id, fields):
            return [SimpleNamespace(host_id="host-1")]

    class _RmsApiMock:
        def __init__(self, client):
            pass

        def get_evaluators(self, host_id, fields):
            return []

    monkeypatch.setattr("ansys.hps.client.jms.ProjectApi", _ProjectApiMock)
    monkeypatch.setattr("ansys.hps.client.rms.RmsApi", _RmsApiMock)

    client = MonitorApi(_make_hps_client(url=BASE_URL))
    with pytest.raises(ClientError, match="Could not resolve evaluator"):
        client._resolve_evaluator_name_for_task("task-abc", "proj-123")


def test_resolve_evaluator_name_for_task_raises_when_evaluator_name_missing(monkeypatch):
    class _ProjectApiMock:
        def __init__(self, client, project_id):
            pass

        def get_tasks(self, id, fields):
            return [SimpleNamespace(host_id="host-1")]

    class _RmsApiMock:
        def __init__(self, client):
            pass

        def get_evaluators(self, host_id, fields):
            return [SimpleNamespace(name="")]

    monkeypatch.setattr("ansys.hps.client.jms.ProjectApi", _ProjectApiMock)
    monkeypatch.setattr("ansys.hps.client.rms.RmsApi", _RmsApiMock)

    client = MonitorApi(_make_hps_client(url=BASE_URL))
    with pytest.raises(ClientError, match="does not provide a name"):
        client._resolve_evaluator_name_for_task("task-abc", "proj-123")


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

    monkeypatch.setitem(
        sys.modules, "websocket", SimpleNamespace(create_connection=fake_create_connection)
    )

    client = MonitorApi(_make_hps_client(url=BASE_URL))
    client.send_ws_command({"type": "command"})

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

    monkeypatch.setitem(
        sys.modules, "websocket", SimpleNamespace(create_connection=fake_create_connection)
    )

    client = MonitorApi(
        _make_hps_client(url=BASE_URL, access_token="jwt"),
        timeout_seconds=7.5,
        ws_connection_options={
            "sslopt": {"cert_reqs": 0},
            "header": {"X-Test": "ok"},
        },
    )
    client.send_ws_command({"type": "command"})

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

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="jwt"))
    topics = client.list_topics(limit=50)

    sent = ws.sent[0]
    assert sent["type"] == "command"
    assert sent["action"] == "list_tags"
    assert sent["limit"] == 50
    assert sent["token"] == "jwt"
    assert topics == {"task_id": ["t1", "t2"], "status": ["RUNNING", "COMPLETED"]}


def test_list_topics_empty_tags_response(monkeypatch):
    """Server returns empty tags dict."""
    _make_ws_mock(monkeypatch, {"tags": {}})

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    topics = client.list_topics(WS_TOPICS_URL)

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

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    topics = client.list_topics(WS_TOPICS_URL)

    assert topics == {}


def test_list_topics_missing_tags_key_in_response(monkeypatch):
    """Server response has no 'tags' key — list_topics returns empty dict."""
    _make_ws_mock(monkeypatch, {"type": "response", "status": "ok"})

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    topics = client.list_topics(WS_TOPICS_URL)

    assert topics == {}


def test_list_topics_can_keep_noisy_keys_when_requested(monkeypatch):
    _make_ws_mock(
        monkeypatch,
        {"tag_list": {"timestamp": ["t1", "t2"], "level": ["info"]}},
    )

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    topics = client.list_topics(WS_TOPICS_URL, exclude_noisy=False)

    assert "timestamp" in topics
    assert topics["level"] == ["info"]


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

    client = MonitorApi(_make_hps_client(url=BASE_URL_HTTPS, access_token="t"))
    topics = client.list_topics(limit=25)

    assert topics == {}
    assert captured["url"] == WSS_TOPICS_URL


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

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="jwt"))
    monkeypatch.setattr(
        client,
        "_resolve_evaluator_name_for_task",
        lambda task_id, project_id: "eval-1",
    )
    list(client.stream_task_host_resources("task-abc", "proj-123"))

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

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    monkeypatch.setattr(
        client,
        "_resolve_evaluator_name_for_task",
        lambda task_id, project_id: "eval-1",
    )
    results = list(client.stream_task_host_resources("task-abc", "proj-123", max_messages=10))

    assert results == updates


def test_stream_task_host_resources_unwraps_messages_envelope(monkeypatch):
    envelopes = [{"messages": [{"cpu_percent": 10.0}, {"cpu_percent": 20.0}]}]
    _make_multi_ws_mock(monkeypatch, envelopes)

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    monkeypatch.setattr(
        client,
        "_resolve_evaluator_name_for_task",
        lambda task_id, project_id: "eval-1",
    )
    results = list(client.stream_task_host_resources("task-abc", "proj-123", max_messages=10))

    assert results == [{"cpu_percent": 10.0}, {"cpu_percent": 20.0}]


def test_stream_task_host_resources_stops_cleanly_on_websocket_timeout(monkeypatch):
    class WebSocketTimeoutException(Exception):  # noqa: N818
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

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    monkeypatch.setattr(
        client,
        "_resolve_evaluator_name_for_task",
        lambda task_id, project_id: "eval-1",
    )
    results = list(client.stream_task_host_resources("task-abc", "proj-123", max_messages=10))

    assert results == []


def test_stream_task_host_resources_respects_backlog(monkeypatch):
    """backlog parameter is forwarded in the subscribe command."""
    ws = _make_multi_ws_mock(monkeypatch, [])

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    monkeypatch.setattr(
        client,
        "_resolve_evaluator_name_for_task",
        lambda task_id, project_id: "eval-1",
    )
    list(client.stream_task_host_resources("task-abc", "proj-123", backlog=42))

    assert ws.sent[0]["backlog"] == {"limit": 42}


def test_stream_task_host_resources_respects_max_messages(monkeypatch):
    """max_messages caps the number of yielded updates."""
    updates = [{"cpu_percent": float(i)} for i in range(10)]
    _make_multi_ws_mock(monkeypatch, updates)

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    monkeypatch.setattr(
        client,
        "_resolve_evaluator_name_for_task",
        lambda task_id, project_id: "eval-1",
    )
    results = list(client.stream_task_host_resources("task-abc", "proj-123", max_messages=3))

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

    client = MonitorApi(_make_hps_client(url=BASE_URL_HTTPS, access_token="t"))
    monkeypatch.setattr(
        client,
        "_resolve_evaluator_name_for_task",
        lambda task_id, project_id: "eval-1",
    )
    list(client.stream_task_host_resources("task-abc", "proj-123"))

    assert captured["url"] == WSS_TOPICS_URL


def test_stream_task_host_resources_raises_when_evaluator_resolution_fails(monkeypatch):
    _make_multi_ws_mock(monkeypatch, [])

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    monkeypatch.setattr(
        client,
        "_resolve_evaluator_name_for_task",
        lambda task_id, project_id: (_ for _ in ()).throw(ClientError("not found")),
    )

    with pytest.raises(ClientError, match="not found"):
        list(client.stream_task_host_resources("task-abc", "proj-123"))


def test_stream_task_logs_unlimited_when_max_messages_none(monkeypatch):
    """max_messages=None should stream until server closes connection."""
    updates = [{"message": "a"}, {"message": "b"}, {"message": "c"}]
    _make_multi_ws_mock(monkeypatch, updates)

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    results = list(client.stream_task_logs("task-abc", max_messages=None))

    assert results == updates


# ---------------------------------------------------------------------------
# stream_scheduler_job_status tests
# ---------------------------------------------------------------------------


def test_stream_scheduler_job_status_sends_correct_topic(monkeypatch):
    """stream_scheduler_job_status subscribes with the correct topic tags."""
    ws = _make_multi_ws_mock(monkeypatch, [{"message": '{"running": 2, "pending": 1}'}])

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="jwt"))
    list(client.stream_scheduler_job_status("taskdef-abc"))

    sent = ws.sent[0]
    assert sent["type"] == "command"
    assert sent["action"] == "subscribe"
    assert sent["token"] == "jwt"
    topic = sent["topics"][0]
    assert topic["client_type"] == "ansys.rep.scaling"
    assert topic["type"] == "metric"
    assert topic["task_definition_id"] == "taskdef-abc"
    assert topic["metric_type"] == "scaler_instances"


def test_stream_scheduler_job_status_yields_messages(monkeypatch):
    """stream_scheduler_job_status yields each status update as it arrives."""
    updates = [
        {"message": '{"running": 2, "pending": 1, "total": 3}'},
        {"message": '{"running": 3, "pending": 0, "total": 3}'},
        {"message": '{"running": 1, "pending": 2, "total": 3}'},
    ]
    _make_multi_ws_mock(monkeypatch, updates)

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    results = list(client.stream_scheduler_job_status("taskdef-abc", max_messages=10))

    assert results == updates


def test_stream_scheduler_job_status_unwraps_messages_envelope(monkeypatch):
    """Messages nested in an envelope dict are unwrapped correctly."""
    envelopes = [
        {
            "messages": [
                {"message": '{"running": 2}'},
                {"message": '{"running": 3}'},
            ]
        }
    ]
    _make_multi_ws_mock(monkeypatch, envelopes)

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    results = list(client.stream_scheduler_job_status("taskdef-abc", max_messages=10))

    assert results == [{"message": '{"running": 2}'}, {"message": '{"running": 3}'}]


def test_stream_scheduler_job_status_stops_cleanly_on_websocket_timeout(monkeypatch):
    """A WebSocketTimeoutException stops iteration cleanly with no messages."""

    class WebSocketTimeoutException(Exception):  # noqa: N818
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

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    results = list(client.stream_scheduler_job_status("taskdef-abc", max_messages=10))

    assert results == []


def test_stream_scheduler_job_status_respects_backlog(monkeypatch):
    """backlog parameter is forwarded in the subscribe command."""
    ws = _make_multi_ws_mock(monkeypatch, [])

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    list(client.stream_scheduler_job_status("taskdef-abc", backlog=50))

    assert ws.sent[0]["backlog"] == {"limit": 50}


def test_stream_scheduler_job_status_respects_max_messages(monkeypatch):
    """max_messages caps the number of yielded updates."""
    updates = [{"message": f'{{"running": {i}}}'} for i in range(10)]
    _make_multi_ws_mock(monkeypatch, updates)

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    results = list(client.stream_scheduler_job_status("taskdef-abc", max_messages=4))

    assert len(results) == 4


def test_stream_scheduler_job_status_uses_derived_ws_url(monkeypatch):
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

    client = MonitorApi(_make_hps_client(url=BASE_URL_HTTPS, access_token="t"))
    list(client.stream_scheduler_job_status("taskdef-abc"))

    assert captured["url"] == WSS_TOPICS_URL


# ---------------------------------------------------------------------------
# stream_task_logs tests
# ---------------------------------------------------------------------------


def test_stream_task_logs_sends_correct_topic(monkeypatch):
    """stream_task_logs subscribes with the correct topic tags."""
    ws = _make_multi_ws_mock(monkeypatch, [{"message": "log line 1"}])

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="jwt"))
    list(client.stream_task_logs("task-abc"))

    sent = ws.sent[0]
    assert sent["type"] == "command"
    assert sent["action"] == "subscribe"
    assert sent["token"] == "jwt"
    topic = sent["topics"][0]
    assert topic["task_id"] == "task-abc"
    assert topic["client_type"] == "ansys.rep.evaluator.file_tail"


def test_stream_task_logs_includes_file_path_when_provided(monkeypatch):
    """stream_task_logs includes file_path in topic when specified."""
    ws = _make_multi_ws_mock(monkeypatch, [])

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    list(client.stream_task_logs("task-abc", file_path="console_output.txt"))

    topic = ws.sent[0]["topics"][0]
    assert topic["file_path"] == "console_output.txt"


def test_stream_task_logs_omits_file_path_when_not_provided(monkeypatch):
    """stream_task_logs does not include file_path when not specified."""
    ws = _make_multi_ws_mock(monkeypatch, [])

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    list(client.stream_task_logs("task-abc"))

    topic = ws.sent[0]["topics"][0]
    assert "file_path" not in topic


def test_stream_task_logs_yields_messages(monkeypatch):
    """stream_task_logs yields each log message as it arrives."""
    messages = [
        {"message": "line 1", "timestamp": "2026-06-29T10:00:00Z"},
        {"message": "line 2", "timestamp": "2026-06-29T10:00:01Z"},
        {"message": "line 3", "timestamp": "2026-06-29T10:00:02Z"},
    ]
    _make_multi_ws_mock(monkeypatch, messages)

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    results = list(client.stream_task_logs("task-abc"))

    assert results == messages


def test_stream_task_logs_respects_backlog(monkeypatch):
    """backlog parameter is forwarded in the subscribe command."""
    ws = _make_multi_ws_mock(monkeypatch, [])

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    list(client.stream_task_logs("task-abc", backlog=500))

    assert ws.sent[0]["backlog"] == {"limit": 500}


def test_stream_task_logs_respects_max_messages(monkeypatch):
    """max_messages caps the number of yielded log lines."""
    messages = [{"message": f"line {i}"} for i in range(10)]
    _make_multi_ws_mock(monkeypatch, messages)

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    results = list(client.stream_task_logs("task-abc", max_messages=5))

    assert len(results) == 5


def test_stream_task_logs_uses_derived_ws_url(monkeypatch):
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

    client = MonitorApi(_make_hps_client(url=BASE_URL_HTTPS, access_token="t"))
    list(client.stream_task_logs("task-abc"))

    assert captured["url"] == WSS_TOPICS_URL


def test_resolve_project_id_for_task_reads_from_tags(monkeypatch):
    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    monkeypatch.setattr(
        client,
        "stream_task_logs",
        lambda **kwargs: iter(
            [
                {"message": "line", "tags": {"project_id": "proj-123", "task_id": "task-abc"}},
            ]
        ),
    )

    project_id = client.resolve_project_id_for_task("task-abc")

    assert project_id == "proj-123"


def test_resolve_project_id_for_task_reads_top_level_fallback(monkeypatch):
    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    monkeypatch.setattr(
        client,
        "stream_task_logs",
        lambda **kwargs: iter(
            [
                {"message": "line", "project_id": "proj-abc"},
            ]
        ),
    )

    project_id = client.resolve_project_id_for_task("task-abc")

    assert project_id == "proj-abc"


def test_resolve_project_id_for_task_raises_when_missing(monkeypatch):
    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    monkeypatch.setattr(
        client,
        "stream_task_logs",
        lambda **kwargs: iter(
            [
                {"message": "line", "tags": {"task_id": "task-abc"}},
                {"message": "line2"},
            ]
        ),
    )

    with pytest.raises(ClientError, match="Could not infer project_id"):
        client.resolve_project_id_for_task("task-abc")


def test_resolve_project_id_for_task_skips_non_dict_messages(monkeypatch):
    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    monkeypatch.setattr(
        client,
        "stream_task_logs",
        lambda **kwargs: iter(
            [
                "plain-text",
                {"tags": {"project_id": "proj-xyz"}},
            ]
        ),
    )

    project_id = client.resolve_project_id_for_task("task-abc")

    assert project_id == "proj-xyz"


def test_send_ws_command_handles_list_payload_and_skips_non_dict_entries(monkeypatch):
    class _WebSocketMock:
        def __init__(self):
            self.sent = []
            self._recv_messages = [json.dumps([{"id": 1}, "skip", {"id": 2}]), ""]

        def send(self, payload):
            self.sent.append(payload)

        def recv(self):
            return self._recv_messages.pop(0)

        def close(self):
            return None

    ws = _WebSocketMock()
    monkeypatch.setitem(
        sys.modules, "websocket", SimpleNamespace(create_connection=lambda url, **kwargs: ws)
    )

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    results = client.send_ws_command(
        {"type": "command"},
        max_messages=10,
    )

    assert results == [{"id": 1}, {"id": 2}]


def test_send_ws_command_reraises_non_timeout_websocket_error(monkeypatch):
    class _WebSocketMock:
        def send(self, payload):
            pass

        def recv(self):
            raise RuntimeError("boom")

        def close(self):
            return None

    monkeypatch.setitem(
        sys.modules,
        "websocket",
        SimpleNamespace(create_connection=lambda url, **kwargs: _WebSocketMock()),
    )

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    with pytest.raises(RuntimeError, match="boom"):
        client.send_ws_command({"type": "command"})


# ---------------------------------------------------------------------------
# stream_task_process_tree tests
# ---------------------------------------------------------------------------


def test_stream_task_process_tree_sends_correct_topic(monkeypatch):
    """stream_task_process_tree subscribes with the correct topic tags."""
    ws = _make_multi_ws_mock(monkeypatch, [{"processes": [{"pid": 1234}]}])

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="jwt"))
    list(client.stream_task_process_tree("task-abc"))

    sent = ws.sent[0]
    assert sent["type"] == "command"
    assert sent["action"] == "subscribe"
    assert sent["token"] == "jwt"
    topic = sent["topics"][0]
    assert topic["task_id"] == "task-abc"
    assert topic["client_type"] == "ansys.rep.evaluator"
    assert topic["type"] == "metric"
    assert topic["statistic"] == "process_tree"


def test_stream_task_process_tree_yields_messages(monkeypatch):
    """stream_task_process_tree yields each process tree snapshot as it arrives."""
    snapshots = [
        {"processes": [{"pid": 1234, "name": "solver", "cpu_percent": 42.0}]},
        {"processes": [{"pid": 1234, "name": "solver", "cpu_percent": 45.5}]},
        {"processes": [{"pid": 1234, "name": "solver", "cpu_percent": 40.1}]},
    ]
    _make_multi_ws_mock(monkeypatch, snapshots)

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    results = list(client.stream_task_process_tree("task-abc", max_messages=10))

    assert results == snapshots


def test_stream_task_process_tree_respects_backlog(monkeypatch):
    """backlog parameter is forwarded in the subscribe command."""
    ws = _make_multi_ws_mock(monkeypatch, [])

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    list(client.stream_task_process_tree("task-abc", backlog=75))

    assert ws.sent[0]["backlog"] == {"limit": 75}


def test_stream_task_process_tree_respects_max_messages(monkeypatch):
    """max_messages caps the number of yielded snapshots."""
    snapshots = [{"processes": []} for _ in range(10)]
    _make_multi_ws_mock(monkeypatch, snapshots)

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    results = list(client.stream_task_process_tree("task-abc", max_messages=6))

    assert len(results) == 6


def test_stream_task_process_tree_uses_derived_ws_url(monkeypatch):
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

    client = MonitorApi(_make_hps_client(url=BASE_URL_HTTPS, access_token="t"))
    list(client.stream_task_process_tree("task-abc"))

    assert captured["url"] == WSS_TOPICS_URL


def test_stream_task_process_tree_stops_cleanly_on_websocket_timeout(monkeypatch):
    """A WebSocketTimeoutException stops iteration cleanly with no messages."""

    class WebSocketTimeoutException(Exception):  # noqa: N818
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

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    results = list(client.stream_task_process_tree("task-abc", max_messages=10))

    assert results == []


# ---------------------------------------------------------------------------
# get_task_process_tree tests
# ---------------------------------------------------------------------------


def test_get_task_process_tree_returns_list_of_snapshots(monkeypatch):
    """get_task_process_tree collects and returns all snapshots as a list."""
    snapshots = [
        {"processes": [{"pid": 1234, "cpu_percent": 40.0}]},
        {"processes": [{"pid": 1234, "cpu_percent": 42.5}]},
        {"processes": [{"pid": 1234, "cpu_percent": 41.0}]},
    ]
    _make_multi_ws_mock(monkeypatch, snapshots)

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    results = client.get_task_process_tree("task-abc")

    assert isinstance(results, list)
    assert results == snapshots


def test_get_task_process_tree_respects_max_messages_default(monkeypatch):
    """get_task_process_tree uses max_messages=200 by default."""
    # Create 300 messages to verify that only 200 are collected
    snapshots = [{"processes": [{"pid": i}]} for i in range(300)]
    _make_multi_ws_mock(monkeypatch, snapshots)

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    results = client.get_task_process_tree("task-abc")

    assert len(results) == 200


def test_get_task_process_tree_respects_custom_max_messages(monkeypatch):
    """get_task_process_tree respects custom max_messages parameter."""
    snapshots = [{"processes": []} for _ in range(50)]
    _make_multi_ws_mock(monkeypatch, snapshots)

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    results = client.get_task_process_tree("task-abc", max_messages=30)

    assert len(results) == 30


def test_get_task_process_tree_respects_backlog(monkeypatch):
    """backlog parameter is forwarded to stream_task_process_tree."""
    ws = _make_multi_ws_mock(monkeypatch, [])

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    client.get_task_process_tree("task-abc", backlog=150)

    assert ws.sent[0]["backlog"] == {"limit": 150}


def test_get_task_process_tree_uses_derived_ws_url(monkeypatch):
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

    client = MonitorApi(_make_hps_client(url=BASE_URL_HTTPS, access_token="t"))
    client.get_task_process_tree("task-abc")

    assert captured["url"] == WSS_TOPICS_URL


def test_get_task_process_tree_empty_result(monkeypatch):
    """get_task_process_tree returns empty list when server sends no messages."""
    _make_multi_ws_mock(monkeypatch, [])

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    results = client.get_task_process_tree("task-abc")

    assert results == []


# ---------------------------------------------------------------------------
# stream_service_logs tests
# ---------------------------------------------------------------------------


def test_stream_service_logs_sends_correct_topic(monkeypatch):
    """stream_service_logs subscribes with the correct client_type tag."""
    ws = _make_multi_ws_mock(monkeypatch, [{"message": "service log entry"}])

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="jwt"))
    list(client.stream_service_logs("ansys.rep.jms"))

    sent = ws.sent[0]
    assert sent["type"] == "command"
    assert sent["action"] == "subscribe"
    assert sent["token"] == "jwt"
    topic = sent["topics"][0]
    assert topic["client_type"] == "ansys.rep.jms"


def test_stream_service_logs_yields_messages(monkeypatch):
    """stream_service_logs yields each service log message as it arrives."""
    messages = [
        {"message": "Job submitted", "timestamp": "2026-06-29T10:00:00Z"},
        {"message": "Job started", "timestamp": "2026-06-29T10:00:05Z"},
        {"message": "Job completed", "timestamp": "2026-06-29T10:00:30Z"},
    ]
    _make_multi_ws_mock(monkeypatch, messages)

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    results = list(client.stream_service_logs("ansys.rep.jms"))

    assert results == messages


def test_stream_service_logs_respects_backlog(monkeypatch):
    """backlog parameter is forwarded in the subscribe command."""
    ws = _make_multi_ws_mock(monkeypatch, [])

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    list(client.stream_service_logs("ansys.rep.jms", backlog=250))

    assert ws.sent[0]["backlog"] == {"limit": 250}


def test_stream_service_logs_respects_max_messages(monkeypatch):
    """max_messages caps the number of yielded messages."""
    messages = [{"message": f"entry {i}"} for i in range(20)]
    _make_multi_ws_mock(monkeypatch, messages)

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    results = list(client.stream_service_logs("ansys.rep.jms", max_messages=7))

    assert len(results) == 7


def test_stream_service_logs_with_different_client_types(monkeypatch):
    """stream_service_logs works with different service client_type values."""
    ws = _make_multi_ws_mock(monkeypatch, [{"message": "scaling event"}])

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    list(client.stream_service_logs("ansys.rep.scaling"))

    topic = ws.sent[0]["topics"][0]
    assert topic["client_type"] == "ansys.rep.scaling"


def test_stream_service_logs_uses_derived_ws_url(monkeypatch):
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

    client = MonitorApi(_make_hps_client(url=BASE_URL_HTTPS, access_token="t"))
    list(client.stream_service_logs("ansys.rep.jms"))

    assert captured["url"] == WSS_TOPICS_URL


def test_stream_service_logs_stops_cleanly_on_websocket_timeout(monkeypatch):
    """A WebSocketTimeoutException stops iteration cleanly with no messages."""

    class WebSocketTimeoutException(Exception):  # noqa: N818
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

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    results = list(client.stream_service_logs("ansys.rep.jms", max_messages=10))

    assert results == []
