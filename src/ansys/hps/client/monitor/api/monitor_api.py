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

    def list_topics(self, limit: int = 1000) -> dict[str, set[str]]:
        """Discover all tag keys and their observed values from recent log entries.

        Queries log messages without filters and aggregates unique tag keys and
        values found in the responses.  Only entries present in the log store at
        call time are reflected in the result.

        Args:
            limit: Maximum number of log entries to inspect.

        Returns:
            Dictionary mapping each tag key to the set of values seen for that key.
        """
        data = self.query_logs({"limit": limit})

        # Response may be a list or a dict with a list under a known key
        if isinstance(data, list):
            entries = data
        elif isinstance(data, dict):
            # Try common envelope keys
            entries = data.get("logs") or data.get("items") or data.get("results") or []
        else:
            entries = []

        topics: dict[str, set[str]] = {}
        for entry in entries:
            # Tags may live under a "tags" sub-dict or as "tag:<key>" top-level keys
            tags: dict[str, Any] = {}
            if isinstance(entry, dict):
                if "tags" in entry and isinstance(entry["tags"], dict):
                    tags = entry["tags"]
                else:
                    tags = {
                        k[4:]: v
                        for k, v in entry.items()
                        if k.startswith("tag:") and isinstance(v, str)
                    }
            for key, value in tags.items():
                topics.setdefault(key, set()).add(str(value))

        return topics

    def send_ws_command(
        self, ws_url: str, command: dict[str, Any], max_messages: int = 1
    ) -> list[dict[str, Any]]:
        try:
            from websocket import create_connection
        except ImportError as exc:  # pragma: no cover - runtime dependency guard
            raise RuntimeError(
                "websocket-client is required for websocket commands. "
                "Install dependencies from requirements.txt."
            ) from exc

        if self.token and "token" not in command:
            command = {**command, "token": self.token}

        responses: list[dict[str, Any]] = []
        ws = create_connection(ws_url, timeout=self.timeout_seconds)
        try:
            ws.send(json.dumps(command))
            for _ in range(max_messages):
                raw = ws.recv()
                if not raw:
                    break
                responses.append(json.loads(raw))
        finally:
            ws.close()
        return responses


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
