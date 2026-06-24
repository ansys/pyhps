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

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from collections.abc import Generator
from dataclasses import dataclass
from typing import Any


@dataclass
class MonitorClient:
    """Client for monitor query interfaces.

    Attributes:
        base_url: Base URL for REST endpoints (for example ``http://localhost:1089``).
        token: Optional JWT token used for authenticated REST/WebSocket requests.
        timeout_seconds: Timeout used for network operations.

    Methods:
        get_build_info: Fetch build metadata from the REST API.
        query_logs: Query log messages via REST filters.
        send_ws_command: Send a command payload to the WebSocket topics endpoint.
    """

    base_url: str
    token: str | None = None
    timeout_seconds: float = 10.0

    def _auth_headers(self) -> dict[str, str]:
        if not self.token:
            return {}
        return {"Authorization": "Bearer " + self.token}

    def get_build_info(self) -> dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}/dcs/monitor/api/"
        req = urllib.request.Request(url, headers=self._auth_headers(), method="GET")
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def query_logs(self, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        filters = filters or {}
        params: dict[str, str] = {}
        for key, value in filters.items():
            if isinstance(value, list):
                params[key] = ",".join(str(v) for v in value)
            else:
                params[key] = str(value)

        query = urllib.parse.urlencode(params)
        url = f"{self.base_url.rstrip('/')}/dcs/monitor/api/log"
        if query:
            url = f"{url}?{query}"

        req = urllib.request.Request(url, headers=self._auth_headers(), method="GET")
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def list_topics(self, ws_url: str, limit: int = 1000) -> dict[str, list[str]]:
        """List all known tag keys and their values via the WebSocket ``list_tags`` action.

        Sends a ``list_tags`` command to the monitor WebSocket endpoint and returns
        the authoritative tag catalogue reported by the server.

        Args:
            ws_url: Full WebSocket URL, e.g.
                ``wss://localhost:8443/hps/dcs/monitor/ws/topics``.
            limit: Maximum number of tag values to request per key.

        Returns:
            Dictionary mapping each tag key to a list of known values as returned
            by the server.
        """
        command = {
            "type": "command",
            "action": "list_tags",
            "limit": limit,
        }
        responses = self.send_ws_command(ws_url, command, max_messages=1)
        if not responses:
            return {}
        # Expected response shape: {"tags": {"task_id": [...], "status": [...], ...}}
        return responses[0].get("tags", {})

    def send_ws_command(
        self, ws_url: str, command: dict[str, Any], max_messages: int = 1
    ) -> list[dict[str, Any]]:
        return list(self._stream_ws(ws_url, command, max_messages))

    def _ws_url(self) -> str:
        """Derive the WebSocket topics URL from ``base_url``."""
        base = self.base_url.rstrip("/")
        # Replace http(s) scheme with ws(s)
        if base.startswith("https://"):
            base = "wss://" + base[len("https://"):]
        elif base.startswith("http://"):
            base = "ws://" + base[len("http://"):]
        return f"{base}/dcs/monitor/ws/topics"

    def _subscribe_command(
        self,
        topics: list[dict[str, str]],
        backlog: int = 100,
    ) -> dict[str, Any]:
        """Build a WebSocket ``subscribe`` command payload."""
        return {
            "type": "command",
            "action": "subscribe",
            "topics": topics,
            "backlog": {"limit": backlog},
        }

    def stream_service_logs(
        self,
        service: str,
        *,
        ws_url: str | None = None,
        backlog: int = 100,
        max_messages: int = 500,
    ) -> Generator[dict[str, Any], None, None]:
        """Stream log messages for a named HPS service.

        Subscribes to log messages tagged with ``service=<service>`` and yields
        each message as it arrives.

        Args:
            service: Service name to filter on, e.g. ``"jms"``, ``"rms"``,
                ``"housekeeper"``.
            ws_url: WebSocket URL override.  Defaults to the URL derived from
                ``base_url``.
            backlog: Number of historical messages to request on connect.
            max_messages: Maximum total messages to yield before closing the
                connection.

        Yields:
            Parsed JSON message dicts from the server.
        """
        url = ws_url or self._ws_url()
        command = self._subscribe_command(
            topics=[{"service": service}],
            backlog=backlog,
        )
        yield from self._stream_ws(url, command, max_messages)

    def stream_task_logs(
        self,
        task_id: str,
        *,
        ws_url: str | None = None,
        backlog: int = 100,
        max_messages: int = 500,
    ) -> Generator[dict[str, Any], None, None]:
        """Stream log file messages for a specific task.

        Subscribes to log messages tagged with ``task_id=<task_id>`` and yields
        each message as it arrives.  This covers stdout/stderr and any log files
        the task runtime emits to the monitor.

        Args:
            task_id: The task identifier to filter on.
            ws_url: WebSocket URL override.  Defaults to the URL derived from
                ``base_url``.
            backlog: Number of historical messages to request on connect.
            max_messages: Maximum total messages to yield before closing the
                connection.

        Yields:
            Parsed JSON message dicts from the server.
        """
        url = ws_url or self._ws_url()
        command = self._subscribe_command(
            topics=[{"task_id": task_id}],
            backlog=backlog,
        )
        yield from self._stream_ws(url, command, max_messages)

    def get_task_process_tree(
        self,
        task_id: str,
        *,
        ws_url: str | None = None,
        backlog: int = 100,
        max_messages: int = 200,
    ) -> list[dict[str, Any]]:
        """Return process tree messages for a specific task.

        Subscribes to messages tagged with both ``task_id=<task_id>`` and
        ``type=process_tree`` and collects up to ``max_messages`` responses.

        Args:
            task_id: The task identifier to query.
            ws_url: WebSocket URL override.  Defaults to the URL derived from
                ``base_url``.
            backlog: Number of historical messages to request on connect.
            max_messages: Upper bound on messages to collect.

        Returns:
            List of process-tree message dicts as returned by the server.
        """
        url = ws_url or self._ws_url()
        command = self._subscribe_command(
            topics=[{"task_id": task_id, "type": "process_tree"}],
            backlog=backlog,
        )
        return list(self._stream_ws(url, command, max_messages))

    def _stream_ws(
        self,
        ws_url: str,
        command: dict[str, Any],
        max_messages: int,
    ) -> Generator[dict[str, Any], None, None]:
        """Internal generator: connect, send *command*, yield up to *max_messages*."""
        try:
            from websocket import create_connection
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "websocket-client is required for websocket commands. "
                "Install dependencies from requirements.txt."
            ) from exc

        if self.token and "token" not in command:
            command = {**command, "token": self.token}

        ws = create_connection(ws_url, timeout=self.timeout_seconds)
        try:
            ws.send(json.dumps(command))
            for _ in range(max_messages):
                raw = ws.recv()
                if not raw:
                    break
                yield json.loads(raw)
        finally:
            ws.close()


def build_filter_templates(fields: list[str]) -> dict[str, dict[str, Any]]:
    """Create copy/paste REST and WebSocket filter templates.

    Args:
        fields: Tag field names to include in the generated filter objects.

    Returns:
        Dictionary with:
          - ``rest``: query path and query-parameter template using ``tag:<field>`` keys.
          - ``websocket``: topics command payload template for ``subscribe`` requests.
    """
    rest_filters = {f"tag:{field}": ["value"] for field in fields}
    ws_topic = {field: "value" for field in fields}

    return {
        "rest": {
            "path": "/dcs/monitor/api/log",
            "query_params": rest_filters,
        },
        "websocket": {
            "path": "/dcs/monitor/ws/topics",
            "command": {
                "type": "command",
                "action": "subscribe",
                "topics": [ws_topic],
                "backlog": {"limit": 100},
            },
        },
    }
