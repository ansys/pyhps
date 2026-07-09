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

"""Stream HPS service logs with ``MonitorApi.stream_service_logs``.

This example shows how to stream log messages from HPS backend services such as
the Job Management Service (JMS), autoscaling service, or housekeeper tasks using
the monitor WebSocket.

Usage (stream JMS service logs on local/self-signed endpoint):

    python examples/monitor/stream_service_logs.py \\
        --base-url https://localhost:8443/hps \\
        --username repadmin \\
        --password repadmin \\
        --service jms \\
        --insecure

List available services:

    python examples/monitor/stream_service_logs.py \\
        --base-url https://localhost:8443/hps \\
        --username repadmin \\
        --password repadmin \\
        --list-services \\
        --insecure
"""

from __future__ import annotations

import argparse
import json
import ssl
from typing import Any

from ansys.hps.client import Client
from ansys.hps.client.monitor.api.monitor_api import ClientType, MonitorApi


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Stream logs from HPS backend services (JMS, scaling, housekeeper, etc)."
    )
    parser.add_argument("--base-url", default="https://localhost:8443/hps")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument(
        "--service",
        default="jms",
        choices=["jms", "scaling", "housekeeper", "evaluator"],
        help="Service to stream logs from (default: jms).",
    )
    parser.add_argument(
        "--backlog",
        type=int,
        default=100,
        help="Historical messages to request on connect (default: 100).",
    )
    parser.add_argument(
        "--max-messages",
        type=int,
        default=None,
        help="Maximum messages to stream. Omit for unlimited streaming.",
    )
    parser.add_argument(
        "--list-services",
        action="store_true",
        help="List available services and exit.",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification for local/self-signed endpoints.",
    )
    return parser


def _get_client_type(service: str) -> str:
    """Map service name to ClientType constant."""
    service_map = {
        "jms": ClientType.JMS,
        "scaling": ClientType.SCALING,
        "housekeeper": ClientType.HOUSEKEEPER,
        "evaluator": ClientType.EVALUATOR,
    }
    return service_map.get(service, ClientType.JMS)


def _to_text(message: dict[str, Any]) -> str:
    """Normalize monitor payload text for printing."""
    text = message.get("message", "")
    if isinstance(text, str):
        return text
    return json.dumps(text)


def _list_services() -> None:
    """Print available services."""
    print("Available services:")
    print("  jms         - Job Management Service logs")
    print("  scaling     - RMS autoscaling service logs")
    print("  housekeeper - Housekeeper task logs")
    print("  evaluator   - Evaluator state and metrics logs")


def main() -> None:
    args = _build_parser().parse_args()

    if args.list_services:
        _list_services()
        return

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

    # 3) Reuse the same authenticated client in MonitorApi.
    monitor = MonitorApi(
        hps,
        ws_connection_options=ws_options,
        timeout_seconds=30.0,
    )

    client_type = _get_client_type(args.service)
    print(f"Streaming logs from service: {args.service}")
    print("Press Ctrl+C to stop")
    print("-" * 88)

    try:
        # 4) stream_service_logs subscribes to the specified service by client_type.
        for msg in monitor.stream_service_logs(
            client_type=client_type,
            backlog=args.backlog,
            max_messages=args.max_messages,
        ):
            ts = (msg.get("time") or msg.get("timestamp") or "")[:19]
            line = _to_text(msg)
            print(f"{ts} {line}")

    except KeyboardInterrupt:
        print("\nInterrupted by user.")


if __name__ == "__main__":
    main()
