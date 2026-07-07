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
from collections.abc import Generator
from dataclasses import dataclass
from typing import Any

import requests


class ClientType:
    """Known ``client_type`` tag values used by the HPS monitor.

    Pass one of these as the ``client_type`` argument to
    :meth:`MonitorClient.stream_service_logs` or use directly when building
    custom filter topics.

    Attributes:
        FILE_TAIL: Live output lines from a file being tailed on the evaluator.
        EVALUATOR: Evaluator state-machine transitions and metrics stream
            (CPU, memory, process tree, etc.).
        JMS: Job Management Service internal logs.
        SCALING: RMS autoscaling decisions.
        HOUSEKEEPER: Cleanup and housekeeping task logs.

    """

    FILE_TAIL = "ansys.rep.evaluator.file_tail"
    EVALUATOR = "ansys.rep.evaluator"
    JMS = "ansys.rep.jms"
    SCALING = "ansys.rep.scaling"
    HOUSEKEEPER = "ansys.rep.housekeeper"


@dataclass
class MonitorClient:
    """Client for the HPS monitor REST and WebSocket interfaces.

    Attributes:
        base_url: Base URL for REST endpoints, e.g. ``https://localhost:8443/hps``.
            The WebSocket URL is derived automatically from this value.
        token: Optional JWT token used for authenticated REST and WebSocket requests.
        client: Optional pre-authenticated HPS client used for JMS/RMS lookups.
            This is required for evaluator assignment resolution in
            :meth:`stream_task_host_resources`.
        ws_connection_options: Optional keyword arguments forwarded to
            ``websocket.create_connection`` for WebSocket calls. This is useful
            for local/self-signed environments (for example,
            ``{"sslopt": {"cert_reqs": ssl.CERT_NONE}}``).
        timeout_seconds: Timeout in seconds used for all network operations.

    REST methods:
        get_build_info: Fetch build metadata from the monitor REST API.
        query_logs: Query log messages with optional filter parameters.

    WebSocket methods:
        list_topics: List all known tag keys and their values via the
            ``list_tags`` WebSocket action.
        stream_service_logs: Subscribe to and stream log messages filtered by
            ``client_type`` tag.  Use :class:`ClientType` constants for
            well-known services (e.g. ``ClientType.JMS``, ``ClientType.HOUSEKEEPER``).
        stream_task_logs: Subscribe to and stream log messages (stdout, stderr,
            tailed log files) for a specific task, filtered by ``task_id`` and
            optionally ``client_type``.
        resolve_project_id_for_task: Infer ``project_id`` for a task by reading
            one or more task-log messages and extracting ``tags.project_id``.
        get_task_process_tree: Collect process-tree metric snapshots for a specific
            task and return them as a list.
        stream_task_process_tree: Subscribe to and stream process-tree metric
            snapshots for a specific task as they are pushed by the server.
        stream_task_host_resources: Subscribe to and stream CPU and memory metric
            updates for the host running a specific task.
        stream_scheduler_job_status: Subscribe to and stream scheduler job status
            metrics (e.g. Slurm or LSF instance counts) for a task definition.
        send_ws_command: Low-level helper — send any command payload to the
            WebSocket topics endpoint and collect responses.

    Common filter tags:
        ``client_type``, ``task_id``, ``project_id``, ``job_id``,
        ``evaluator_name``, ``host``, ``file_path``, ``level``.
        For metric messages: ``type=metric``, ``statistic`` (e.g. ``process_tree``).

        See :class:`ClientType` for known ``client_type`` values.

    """

    base_url: str
    token: str | None = None
    client: Any | None = None
    ws_connection_options: dict[str, Any] | None = None
    timeout_seconds: float = 10.0

    def _integration_client(self):
        """Return caller-provided authenticated HPS client for JMS/RMS lookups."""
        if self.client is not None:
            return self.client

        raise RuntimeError(
            "A pre-authenticated client is required to resolve evaluator "
            "assignment via JMS/RMS. Pass client=Client(...) to MonitorClient."
        )

    def _resolve_evaluator_name_for_task(self, task_id: str, project_id: str) -> str:
        """Resolve evaluator name for a task using JMS task host_id and RMS evaluator data."""
        from ansys.hps.client.jms import ProjectApi
        from ansys.hps.client.rms import RmsApi

        client = self._integration_client()

        host_id: str | None = None

        tasks = ProjectApi(client, project_id).get_tasks(
            id=task_id,
            fields=["id", "host_id"],
        )
        if tasks:
            host_id = tasks[0].host_id

        if not host_id:
            raise RuntimeError(f"Could not resolve host_id for task '{task_id}' from JMS.")

        rms = RmsApi(client)
        evaluators = rms.get_evaluators(
            host_id=host_id,
            fields=["id", "name", "host_id"],
        )
        if not evaluators:
            raise RuntimeError(f"Could not resolve evaluator for host_id '{host_id}' from RMS.")

        evaluator_name = evaluators[0].name
        if not evaluator_name:
            raise RuntimeError(f"Evaluator for host_id '{host_id}' does not provide a name in RMS.")

        return evaluator_name

    def _auth_headers(self) -> dict[str, str]:
        if not self.token:
            return {}
        return {"Authorization": "Bearer " + self.token}

    def _validated_http_url(self, url: str) -> str:
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Only HTTP(S) URLs are allowed for monitor REST requests.")
        return url

    def get_build_info(self) -> dict[str, Any]:
        url = self._validated_http_url(f"{self.base_url.rstrip('/')}/dcs/monitor/api/")
        response = requests.get(url, headers=self._auth_headers(), timeout=self.timeout_seconds)
        response.raise_for_status()
        return response.json()

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

        safe_url = self._validated_http_url(url)
        response = requests.get(
            safe_url, headers=self._auth_headers(), timeout=self.timeout_seconds
        )
        response.raise_for_status()
        return response.json()

    #: Tag keys that carry a unique value per message and are excluded from
    #: :meth:`list_topics` results by default (``exclude_noisy=True``).
    _NOISY_TAG_KEYS: frozenset[str] = frozenset({"timestamp", "time"})

    #: Tag keys whose value count exceeds this threshold are also treated as
    #: noisy and excluded when ``exclude_noisy=True``.
    _NOISY_MAX_VALUES: int = 100

    def list_topics(
        self,
        ws_url: str | None = None,
        limit: int = 1000,
        exclude_noisy: bool = True,
    ) -> dict[str, list[str]]:
        """List all known tag keys and their values via the WebSocket ``list_tags`` action.

        Sends a ``list_tags`` command to the monitor WebSocket endpoint and returns
        the authoritative tag catalogue reported by the server.

        High-cardinality tag keys (such as ``timestamp``) that carry a unique value
        per message are suppressed by default because they are rarely useful for
        subscription discovery.  Pass ``exclude_noisy=False`` to include them.

        Args:
            ws_url: Optional full WebSocket URL override, e.g.
                ``wss://localhost:8443/hps/monitor/ws/topics``.
                If omitted, this method uses the URL derived from ``base_url``.
            limit: Maximum number of tag values to request per key.
            exclude_noisy: When ``True`` (default), remove tag keys listed in
                :attr:`_NOISY_TAG_KEYS` and any key whose value count exceeds
                :attr:`_NOISY_MAX_VALUES`.

        Returns:
            Dictionary mapping each tag key to a list of known values as returned
            by the server (noisy keys removed unless ``exclude_noisy=False``).

        """
        command = {
            "type": "command",
            "action": "list_tags",
            "limit": limit,
        }
        url = ws_url or self._ws_url()
        responses = self.send_ws_command(url, command, max_messages=1)
        if not responses:
            return {}
        # Server returns {"tag_list": {...}} (not "tags").
        resp = responses[0]
        tags: dict[str, list[str]] = resp.get("tag_list", resp.get("tags", {}))
        if exclude_noisy:
            tags = {
                k: v
                for k, v in tags.items()
                if k not in self._NOISY_TAG_KEYS and len(v) <= self._NOISY_MAX_VALUES
            }
        return tags

    def send_ws_command(
        self, ws_url: str, command: dict[str, Any], max_messages: int | None = 1
    ) -> list[dict[str, Any]]:
        return list(self._stream_ws(ws_url, command, max_messages))

    def _ws_url(self) -> str:
        """Derive the WebSocket topics URL from ``base_url``."""
        base = self.base_url.rstrip("/")
        # Replace http(s) scheme with ws(s)
        if base.startswith("https://"):
            base = "wss://" + base[len("https://") :]
        elif base.startswith("http://"):
            base = "ws://" + base[len("http://") :]
        return f"{base}/monitor/ws/topics"

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
        client_type: str,
        *,
        ws_url: str | None = None,
        backlog: int = 100,
        max_messages: int | None = None,
    ) -> Generator[dict[str, Any], None, None]:
        """Stream log messages for a named HPS service.

        Subscribes to messages filtered by the ``client_type`` tag and yields
        each message as it arrives.  Use :class:`ClientType` constants for
        well-known services::

            for msg in client.stream_service_logs(ClientType.JMS):
                print(msg)

        Args:
            client_type: The ``client_type`` tag value to filter on.  Use a
                :class:`ClientType` constant, e.g. ``ClientType.JMS``,
                ``ClientType.HOUSEKEEPER``, ``ClientType.SCALING``.
            ws_url: WebSocket URL override.  Defaults to the URL derived from
                ``base_url``.
            backlog: Number of historical messages to request on connect.
            max_messages: Maximum total messages to yield before closing the
                connection. Defaults to ``None`` — stream indefinitely until
                interrupted or the server closes the connection.

        Yields:
            Parsed JSON message dicts from the server.

        """
        url = ws_url or self._ws_url()
        command = self._subscribe_command(
            topics=[{"client_type": client_type}],
            backlog=backlog,
        )
        yield from self._stream_ws(url, command, max_messages)

    def stream_task_logs(
        self,
        task_id: str,
        *,
        file_path: str | None = None,
        ws_url: str | None = None,
        backlog: int = 100,
        max_messages: int | None = None,
    ) -> Generator[dict[str, Any], None, None]:
        """Stream log file messages for a specific task.

        Subscribes to messages tagged with ``task_id=<task_id>`` and
        ``client_type=ansys.rep.evaluator.file_tail``, and yields each message
        as it arrives.  Optionally narrows to a single file via ``file_path``.

        Args:
            task_id: The task identifier to filter on.
            file_path: Optional filename to restrict to a single tailed file,
                e.g. ``"console_output.txt"``.
            ws_url: WebSocket URL override.  Defaults to the URL derived from
                ``base_url``.
            backlog: Number of historical messages to request on connect.
            max_messages: Maximum total messages to yield before closing the
                connection. Defaults to ``None`` — stream indefinitely until
                interrupted or the server closes the connection.

        Yields:
            Parsed JSON message dicts from the server.

        """
        url = ws_url or self._ws_url()
        topic: dict[str, str] = {
            "task_id": task_id,
            "client_type": ClientType.FILE_TAIL,
        }
        if file_path is not None:
            topic["file_path"] = file_path
        command = self._subscribe_command(topics=[topic], backlog=backlog)
        yield from self._stream_ws(url, command, max_messages)

    def resolve_project_id_for_task(
        self,
        task_id: str,
        *,
        ws_url: str | None = None,
        backlog: int = 1,
        max_messages: int = 5,
    ) -> str:
        """Infer project ID for a task from task-log message tags.

        This helper reads a small number of task-log messages and extracts
        ``project_id`` from either ``message["tags"]["project_id"]`` (preferred)
        or the top-level ``message["project_id"]`` field when present.

        Args:
            task_id: Task identifier to inspect.
            ws_url: WebSocket URL override. Defaults to the URL derived from
                ``base_url``.
            backlog: Number of historical log messages to request.
            max_messages: Maximum messages to inspect before failing.

        Returns:
            Project identifier associated with ``task_id``.

        Raises:
            RuntimeError: If no inspected message provides a project ID.

        """
        for msg in self.stream_task_logs(
            task_id=task_id,
            ws_url=ws_url,
            backlog=backlog,
            max_messages=max_messages,
        ):
            if not isinstance(msg, dict):
                continue

            tags = msg.get("tags")
            if isinstance(tags, dict):
                project_id = tags.get("project_id")
                if isinstance(project_id, str) and project_id:
                    return project_id

            project_id = msg.get("project_id")
            if isinstance(project_id, str) and project_id:
                return project_id

        raise RuntimeError(
            f"Could not infer project_id for task '{task_id}' from task logs. "
            "Provide project_id explicitly."
        )

    def get_task_process_tree(
        self,
        task_id: str,
        *,
        ws_url: str | None = None,
        backlog: int = 100,
        max_messages: int | None = 200,
    ) -> list[dict[str, Any]]:
        """Return process tree metric messages for a specific task.

        Collects up to ``max_messages`` process-tree snapshots and returns them
        all at once.  Use :meth:`stream_task_process_tree` if you want to react
        to each snapshot as it arrives.

        Args:
            task_id: The task identifier to query.
            ws_url: WebSocket URL override.  Defaults to the URL derived from
                ``base_url``.
            backlog: Number of historical messages to request on connect.
            max_messages: Upper bound on messages to collect. If ``None``,
                collect until interrupted or the server closes the connection.

        Returns:
            List of process-tree message dicts as returned by the server.

        """
        return list(
            self.stream_task_process_tree(
                task_id, ws_url=ws_url, backlog=backlog, max_messages=max_messages
            )
        )

    def stream_task_process_tree(
        self,
        task_id: str,
        *,
        ws_url: str | None = None,
        backlog: int = 100,
        max_messages: int | None = None,
    ) -> Generator[dict[str, Any], None, None]:
        """Stream process tree metric updates for a specific task.

        Subscribes to process-tree metric messages and yields each snapshot as
        the server pushes it.  The server typically pushes a new snapshot on a
        fixed interval while the task is running, allowing you to observe process
        lifecycle in real time::

            for snapshot in client.stream_task_process_tree("task-123"):
                pids = [p["pid"] for p in snapshot.get("processes", [])]
                print(f"Running PIDs: {pids}")

        Args:
            task_id: The task identifier to monitor.
            ws_url: WebSocket URL override.  Defaults to the URL derived from
                ``base_url``.
            backlog: Number of historical snapshots to request on connect.
            max_messages: Maximum total snapshots to yield before closing the
                connection. Defaults to ``None`` — stream indefinitely until
                interrupted or the server closes the connection.

        Yields:
            Parsed JSON process-tree snapshot dicts from the server.

        """
        url = ws_url or self._ws_url()
        command = self._subscribe_command(
            topics=[
                {
                    "task_id": task_id,
                    "client_type": ClientType.EVALUATOR,
                    "type": "metric",
                    "statistic": "process_tree",
                }
            ],
            backlog=backlog,
        )
        yield from self._stream_ws(url, command, max_messages)

    def stream_task_host_resources(
        self,
        task_id: str,
        project_id: str,
        *,
        ws_url: str | None = None,
        backlog: int = 100,
        max_messages: int | None = None,
    ) -> Generator[dict[str, Any], None, None]:
        """Stream CPU and memory metric updates for the host running a specific task.

        Resolves the task's assigned evaluator (via JMS and RMS) and subscribes
        to ``host_resources`` metric messages for that evaluator.
        Yields each update as it arrives::

            for update in client.stream_task_host_resources("task-123", "project-abc"):
                cpu = update.get("cpu_percent")
                mem = update.get("memory_percent")
                print(f"CPU: {cpu}%  Memory: {mem}%")

        Args:
            task_id: The task identifier to monitor.
            project_id: The JMS project identifier that owns ``task_id``.
            ws_url: WebSocket URL override.  Defaults to the URL derived from
                ``base_url``.
            backlog: Number of historical metric messages to request on connect.
            max_messages: Maximum total messages to yield before closing the
                connection. Defaults to ``None`` — stream indefinitely until
                interrupted or the server closes the connection, which is
                the typical usage pattern for host resource monitoring.

        Yields:
            Parsed JSON host-resource metric dicts from the server.

        """
        url = ws_url or self._ws_url()
        evaluator_name = self._resolve_evaluator_name_for_task(task_id, project_id)
        command = self._subscribe_command(
            topics=[
                {
                    "evaluator_name": evaluator_name,
                    "client_type": ClientType.EVALUATOR,
                    "type": "metric",
                    "statistic": "host_resources",
                }
            ],
            backlog=backlog,
        )
        yield from self._stream_ws(url, command, max_messages)

    def stream_scheduler_job_status(
        self,
        task_definition_id: str,
        *,
        ws_url: str | None = None,
        backlog: int = 100,
        max_messages: int | None = None,
    ) -> Generator[dict[str, Any], None, None]:
        """Stream scheduler job status metrics for a task definition.

        Subscribes to ``scaler_instances`` metric messages emitted by the HPS
        autoscaling service (``ansys.rep.scaling``) for a specific task definition.
        Each message represents a status update from the underlying job scheduler
        (e.g. Slurm or LSF) and contains instance-count information for the
        registered scaler::

            for status in client.stream_scheduler_job_status("taskdef-abc"):
                print(status)

        Args:
            task_definition_id: The task definition identifier to monitor.
            ws_url: WebSocket URL override.  Defaults to the URL derived from
                ``base_url``.
            backlog: Number of historical metric messages to request on connect.
            max_messages: Maximum total messages to yield before closing the
                connection. Defaults to ``None`` — stream indefinitely until
                interrupted or the server closes the connection.

        Yields:
            Parsed JSON scheduler job status metric dicts from the server.

        """
        url = ws_url or self._ws_url()
        command = self._subscribe_command(
            topics=[
                {
                    "client_type": ClientType.SCALING,
                    "type": "metric",
                    "task_definition_id": task_definition_id,
                    "metric_type": "scaler_instances",
                }
            ],
            backlog=backlog,
        )
        yield from self._stream_ws(url, command, max_messages)

    def _stream_ws(
        self,
        ws_url: str,
        command: dict[str, Any],
        max_messages: int | None,
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

        connection_options: dict[str, Any] = {"timeout": self.timeout_seconds}
        if self.ws_connection_options:
            connection_options.update(self.ws_connection_options)

        if self.token:
            existing_headers = connection_options.get("header")
            if isinstance(existing_headers, dict):
                connection_options["header"] = {
                    **existing_headers,
                    "Authorization": "Bearer " + self.token,
                }
            else:
                connection_options["header"] = {"Authorization": "Bearer " + self.token}

        ws = create_connection(ws_url, **connection_options)
        try:
            ws.send(json.dumps(command))
            yielded = 0
            while max_messages is None or yielded < max_messages:
                try:
                    raw = ws.recv()
                except Exception as exc:
                    if exc.__class__.__name__ == "WebSocketTimeoutException":
                        break
                    raise
                if not raw:
                    break

                payload = json.loads(raw)
                if isinstance(payload, dict) and isinstance(payload.get("messages"), list):
                    messages = payload["messages"]
                elif isinstance(payload, list):
                    messages = payload
                else:
                    messages = [payload]

                for message in messages:
                    if not isinstance(message, dict):
                        continue
                    yield message
                    yielded += 1
                    if max_messages is not None and yielded >= max_messages:
                        break
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
    ws_topic = dict.fromkeys(fields, "value")

    return {
        "rest": {
            "path": "/dcs/monitor/api/log",
            "query_params": rest_filters,
        },
        "websocket": {
            "path": "/monitor/ws/topics",
            "command": {
                "type": "command",
                "action": "subscribe",
                "topics": [ws_topic],
                "backlog": {"limit": 100},
            },
        },
    }
