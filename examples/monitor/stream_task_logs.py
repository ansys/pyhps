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

"""Stream evaluator file-tail logs for a task with ``MonitorClient.stream_task_logs``.

This example shows the standard monitoring pattern for task output:

1. Authenticate once with ``Client``.
2. Reuse the same token/session in ``MonitorClient``.
3. Subscribe to task log messages by ``task_id``.
4. Optionally narrow output to a specific ``file_path``.

By default, messages are streamed continuously until you stop the program
(``Ctrl+C``).  You can set ``--max-messages`` for a bounded run.

Typical usage (local/self-signed endpoint):

    python examples/monitor/stream_task_logs.py \
        --base-url https://localhost:8443/hps \
        --username repadmin \
        --password repadmin \
        --task-id <TASK_ID> \
        --insecure

Filter to one file only:

    python examples/monitor/stream_task_logs.py \
        --base-url https://localhost:8443/hps \
        --username repadmin \
        --password repadmin \
        --task-id <TASK_ID> \
        --file-path console_output.txt \
        --insecure
"""

from __future__ import annotations

import argparse
import json
import ssl
from typing import Any

from ansys.hps.client import Client
from ansys.hps.client.monitor.api.monitor_api import MonitorClient


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Stream evaluator file-tail logs for a task.")
    parser.add_argument("--base-url", default="https://localhost:8443/hps")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--file-path", default=None, help="Optional single file name to filter.")
    parser.add_argument("--backlog", type=int, default=200)
    parser.add_argument(
        "--max-messages",
        type=int,
        default=None,
        help="Maximum messages to stream. Omit for unlimited streaming.",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification for local/self-signed endpoints.",
    )
    return parser


def _to_text(message: dict[str, Any]) -> str:
    """Normalize monitor payload text for printing."""
    text = message.get("message", "")
    if isinstance(text, str):
        return text
    return json.dumps(text)


def main() -> None:
    args = _build_parser().parse_args()

    # 1) Authenticate once with the top-level HPS client.
    hps = Client(
        args.base_url,
        args.username,
        args.password,
        verify=not args.insecure,
    )

    # 2) Configure websocket options only when running in insecure local mode.
    ws_options: dict[str, Any] | None = None
    if args.insecure:
        ws_options = {"sslopt": {"cert_reqs": ssl.CERT_NONE}}

    # 3) Reuse the same authenticated client in MonitorClient.
    monitor = MonitorClient(
        hps,
        ws_connection_options=ws_options,
        timeout_seconds=30.0,
    )

    print(f"Streaming logs for task {args.task_id}")
    if args.file_path:
        print(f"Filtering file_path={args.file_path}")
    print("Press Ctrl+C to stop")
    print("-" * 88)

    try:
        # 4) stream_task_logs subscribes to task_id + evaluator file-tail client_type.
        for msg in monitor.stream_task_logs(
            task_id=args.task_id,
            file_path=args.file_path,
            backlog=args.backlog,
            max_messages=args.max_messages,
        ):
            ts = (msg.get("time") or msg.get("timestamp") or "")[:19]
            tags = msg.get("tags") or {}
            path = tags.get("file_path", "?")
            line = _to_text(msg)
            print(f"{ts} [{path}] {line}")
    except KeyboardInterrupt:
        print("\nInterrupted by user.")


if __name__ == "__main__":
    main()
