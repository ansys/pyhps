# Copyright (C) 2022 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

import pytest

import ansys.hps.client.monitor.api.monitor_api as monitor_api_module
from ansys.hps.client import ClientError
from ansys.hps.client.monitor import MonitorApi

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


def _make_ws_mock(monkeypatch, response_payload):
    class _WsMock:
        def __init__(self):
            self.sent = []
            self._responses = [json.dumps(response_payload), ""]
            self.closed = False

        def send(self, payload):
            self.sent.append(json.loads(payload))

        def recv(self):
            return self._responses.pop(0) if self._responses else ""

        def close(self):
            self.closed = True

    ws = _WsMock()
    monkeypatch.setitem(
        sys.modules,
        "websocket",
        SimpleNamespace(create_connection=lambda url, **kwargs: ws),
    )
    return ws


def _make_multi_ws_mock(monkeypatch, messages):
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


# ---------------------------------------------------------------------------
# Module-level sanity
# ---------------------------------------------------------------------------


def test_monitor_api_module_reload_executes_definitions():
    reloaded = importlib.reload(monitor_api_module)
    assert reloaded.ClientType.FILE_TAIL == "ansys.rep.evaluator.file_tail"
    assert hasattr(reloaded, "MonitorApi")


# ---------------------------------------------------------------------------
# WebSocket URL derivation
# ---------------------------------------------------------------------------


def test_ws_url_derived_from_http_base_url():
    client = MonitorApi(_make_hps_client(url=BASE_URL))
    assert client.ws_url == WS_TOPICS_URL


def test_ws_url_derived_from_https_base_url():
    client = MonitorApi(_make_hps_client(url=BASE_URL_HTTPS))
    assert client.ws_url == WSS_TOPICS_URL


def test_ws_url_attribute_overrides_derived_url():
    client = MonitorApi(_make_hps_client(url=BASE_URL), ws_url="wss://custom/monitor/ws/topics")
    assert client.ws_url == "wss://custom/monitor/ws/topics"


# ---------------------------------------------------------------------------
# Token and auth header handling in send_ws_command
# ---------------------------------------------------------------------------


def test_send_ws_command_injects_token_and_auth_header(monkeypatch):
    captured = {}

    class _WsMock:
        def __init__(self):
            self.sent = []

        def send(self, payload):
            self.sent.append(payload)

        def recv(self):
            return ""

        def close(self):
            pass

    ws = _WsMock()

    def fake_create_connection(url, **kwargs):
        captured["url"] = url
        captured["header"] = kwargs.get("header")
        captured["timeout"] = kwargs.get("timeout")
        return ws

    monkeypatch.setitem(
        sys.modules, "websocket", SimpleNamespace(create_connection=fake_create_connection)
    )

    client = MonitorApi(_make_hps_client(access_token="jwt"), timeout_seconds=7.0)
    client.send_ws_command({"type": "command", "action": "subscribe"}, max_messages=1)

    sent_command = json.loads(ws.sent[0])
    assert captured["url"] == WS_TOPICS_URL
    assert captured["timeout"] == 7.0
    assert captured["header"] == {"Authorization": "Bearer jwt"}
    assert sent_command["token"] == "jwt"


def test_send_ws_command_preserves_existing_token(monkeypatch):
    class _WsMock:
        def __init__(self):
            self.sent = []

        def send(self, payload):
            self.sent.append(payload)

        def recv(self):
            return ""

        def close(self):
            pass

    ws = _WsMock()
    monkeypatch.setitem(
        sys.modules,
        "websocket",
        SimpleNamespace(create_connection=lambda url, **kwargs: ws),
    )

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="jwt"))
    client.send_ws_command({"type": "command", "token": "already-present"})

    sent_command = json.loads(ws.sent[0])
    assert sent_command["token"] == "already-present"


def test_send_ws_command_no_auth_header_without_token(monkeypatch):
    captured = {}

    monkeypatch.setitem(
        sys.modules,
        "websocket",
        SimpleNamespace(
            create_connection=lambda url, **kwargs: (
                captured.update({"header": kwargs.get("header")}),
                SimpleNamespace(send=lambda p: None, recv=lambda: "", close=lambda: None),
            )[1]
        ),
    )

    client = MonitorApi(_make_hps_client(url=BASE_URL))
    client.send_ws_command({"type": "command"})

    assert captured["header"] is None


def test_send_ws_command_forwards_ws_connection_options_and_merges_auth_header(monkeypatch):
    captured = {}

    monkeypatch.setitem(
        sys.modules,
        "websocket",
        SimpleNamespace(
            create_connection=lambda url, **kwargs: (
                captured.update(kwargs),
                SimpleNamespace(send=lambda p: None, recv=lambda: "", close=lambda: None),
            )[1]
        ),
    )

    client = MonitorApi(
        _make_hps_client(url=BASE_URL, access_token="jwt"),
        timeout_seconds=7.5,
        ws_connection_options={"sslopt": {"cert_reqs": 0}, "header": {"X-Test": "ok"}},
    )
    client.send_ws_command({"type": "command"})

    assert captured["timeout"] == 7.5
    assert captured["sslopt"] == {"cert_reqs": 0}
    assert captured["header"]["X-Test"] == "ok"
    assert captured["header"]["Authorization"] == "Bearer jwt"


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


def test_send_ws_command_reraises_non_timeout_websocket_error(monkeypatch):
    class _WsMock:
        def send(self, payload):
            pass

        def recv(self):
            raise RuntimeError("boom")

        def close(self):
            pass

    monkeypatch.setitem(
        sys.modules,
        "websocket",
        SimpleNamespace(create_connection=lambda url, **kwargs: _WsMock()),
    )

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    with pytest.raises(RuntimeError, match="boom"):
        client.send_ws_command({"type": "command"})


def test_send_ws_command_stops_on_websocket_timeout(monkeypatch):
    class WebSocketTimeoutError(Exception):
        pass

    class _WsMock:
        def send(self, payload):
            pass

        def recv(self):
            raise WebSocketTimeoutError()

        def close(self):
            pass

    monkeypatch.setitem(
        sys.modules,
        "websocket",
        SimpleNamespace(create_connection=lambda url, **kwargs: _WsMock()),
    )

    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    results = client.send_ws_command({"type": "command"}, max_messages=10)
    assert results == []


# ---------------------------------------------------------------------------
# _resolve_evaluator_name_for_task error paths
# ---------------------------------------------------------------------------


def test_integration_client_returns_provided_client():
    provided = SimpleNamespace(name="provided-client")
    assert MonitorApi(provided)._integration_client() is provided


def test_resolve_evaluator_name_for_task_success(monkeypatch):
    client = MonitorApi(_make_hps_client())
    monkeypatch.setattr(
        "ansys.hps.client.jms.ProjectApi",
        lambda c, pid: SimpleNamespace(get_tasks=lambda **kw: [SimpleNamespace(host_id="host-1")]),
    )
    monkeypatch.setattr(
        "ansys.hps.client.rms.RmsApi",
        lambda c: SimpleNamespace(
            get_evaluators=lambda **kw: [SimpleNamespace(name="eval-1", host_id="host-1")]
        ),
    )
    assert client._resolve_evaluator_name_for_task("task-1", "proj-1") == "eval-1"


def test_resolve_evaluator_name_for_task_raises_when_task_not_found(monkeypatch):
    client = MonitorApi(_make_hps_client())
    monkeypatch.setattr(
        "ansys.hps.client.jms.ProjectApi",
        lambda c, pid: SimpleNamespace(get_tasks=lambda **kw: []),
    )
    with pytest.raises(ClientError, match="host_id"):
        client._resolve_evaluator_name_for_task("task-1", "proj-1")


def test_resolve_evaluator_name_for_task_raises_when_no_evaluator(monkeypatch):
    client = MonitorApi(_make_hps_client())
    monkeypatch.setattr(
        "ansys.hps.client.jms.ProjectApi",
        lambda c, pid: SimpleNamespace(get_tasks=lambda **kw: [SimpleNamespace(host_id="host-1")]),
    )
    monkeypatch.setattr(
        "ansys.hps.client.rms.RmsApi",
        lambda c: SimpleNamespace(get_evaluators=lambda **kw: []),
    )
    with pytest.raises(ClientError, match="evaluator"):
        client._resolve_evaluator_name_for_task("task-1", "proj-1")


def test_resolve_evaluator_name_for_task_raises_when_evaluator_name_missing(monkeypatch):
    client = MonitorApi(_make_hps_client())
    monkeypatch.setattr(
        "ansys.hps.client.jms.ProjectApi",
        lambda c, pid: SimpleNamespace(get_tasks=lambda **kw: [SimpleNamespace(host_id="host-1")]),
    )
    monkeypatch.setattr(
        "ansys.hps.client.rms.RmsApi",
        lambda c: SimpleNamespace(
            get_evaluators=lambda **kw: [SimpleNamespace(name=None, host_id="host-1")]
        ),
    )
    with pytest.raises(ClientError, match="name"):
        client._resolve_evaluator_name_for_task("task-1", "proj-1")


# ---------------------------------------------------------------------------
# resolve_project_id_for_task
# ---------------------------------------------------------------------------


def test_resolve_project_id_for_task_reads_from_tags(monkeypatch):
    _make_multi_ws_mock(monkeypatch, [{"tags": {"project_id": "proj-99", "task_id": "t1"}}])
    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    assert client.resolve_project_id_for_task("t1") == "proj-99"


def test_resolve_project_id_for_task_reads_top_level_fallback(monkeypatch):
    _make_multi_ws_mock(monkeypatch, [{"project_id": "proj-fallback"}])
    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    assert client.resolve_project_id_for_task("t1") == "proj-fallback"


def test_resolve_project_id_for_task_raises_when_missing(monkeypatch):
    _make_multi_ws_mock(monkeypatch, [{"no_project_id": True}])
    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    with pytest.raises(ClientError, match="project_id"):
        client.resolve_project_id_for_task("t1", max_messages=1)


# ---------------------------------------------------------------------------
# list_topics noise filtering
# ---------------------------------------------------------------------------


def test_list_topics_filters_noisy_keys(monkeypatch):
    server_response = {
        "tags": {
            "client_type": ["ansys.rep.jms", "ansys.rep.evaluator"],
            "timestamp": ["2024-01-01T00:00:00Z"],
        }
    }
    _make_ws_mock(monkeypatch, server_response)
    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="jwt"))
    topics = client.list_topics()
    assert "client_type" in topics
    assert "timestamp" not in topics


def test_list_topics_can_include_noisy_keys(monkeypatch):
    server_response = {"tags": {"client_type": ["ansys.rep.jms"], "timestamp": ["t1"]}}
    _make_ws_mock(monkeypatch, server_response)
    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="jwt"))
    topics = client.list_topics(exclude_noisy=False)
    assert "timestamp" in topics


# ---------------------------------------------------------------------------
# get_task_process_tree collects list
# ---------------------------------------------------------------------------


def test_get_task_process_tree_collects_snapshots(monkeypatch):
    snapshots = [{"processes": [{"pid": i}]} for i in range(3)]
    _make_multi_ws_mock(monkeypatch, snapshots)
    client = MonitorApi(_make_hps_client(url=BASE_URL, access_token="t"))
    result = client.get_task_process_tree("task-1", max_messages=3)
    assert isinstance(result, list)
    assert len(result) == 3
