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

"""Annotated example: discover available monitor topics with MonitorClient.list_topics.

``list_topics`` sends a ``list_tags`` WebSocket command to the HPS monitor
endpoint and returns a dictionary mapping every known tag key to all currently
active values.  This is useful for exploring what is visible on the WebSocket
bus before building a targeted subscription.

Typical tag keys include:
    - ``task_id``       – IDs of tasks that have active evaluator log streams.
    - ``evaluator_name``– Names of connected evaluators.
    - ``client_type``   – Log source types (e.g. ``ansys.rep.evaluator.file_tail``).
    - ``file_path``     – Log file names being tailed.
    - ``job_id``, ``project_id``, ``status`` – Additional correlation tags.

Usage (local dev with self-signed cert):

    pip install -e .

    python examples/monitor/list_topics.py \\
        --base-url https://localhost:8443/hps \\
        --username repadmin \\
        --password repadmin \\
        --insecure

Pass ``--task-id <ID>`` to further filter the output to rows where that task
appears as a value, or ``--key client_type`` to print only the values for a
single tag key.
"""

from __future__ import annotations

import argparse
import json
import ssl

from ansys.hps.client import Client
from ansys.hps.client.monitor.api.monitor_api import MonitorClient


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="List all available monitor topic tags and their current values."
    )
    parser.add_argument("--base-url", default="https://localhost:8443/hps")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Maximum number of values to request per tag key (default: 1000).",
    )
    parser.add_argument(
        "--key",
        default=None,
        metavar="TAG_KEY",
        help="If set, print only the values for this single tag key.",
    )
    parser.add_argument(
        "--task-id",
        default=None,
        metavar="TASK_ID",
        help="If set, filter and show only tag keys that contain this task ID as a value.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output raw JSON instead of a human-readable table.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="show_all",
        help="Include high-cardinality keys like 'timestamp' that are suppressed by default.",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification for local/self-signed endpoints.",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()

    # 1) Authenticate once with the top-level HPS client.
    hps = Client(
        args.base_url,
        args.username,
        args.password,
        verify=not args.insecure,
    )

    # 2) Configure WebSocket options only when running in insecure local mode.
    ws_options = {"sslopt": {"cert_reqs": ssl.CERT_NONE}} if args.insecure else None

    # 3) Build a MonitorClient that reuses the authenticated client and token.
    #    Supplying client=hps keeps one shared authenticated session for this
    #    script and for monitor methods that also need JMS/RMS lookups.
    monitor = MonitorClient(
        base_url=args.base_url,
        token=hps.access_token,
        client=hps,
        ws_connection_options=ws_options,
        timeout_seconds=30.0,
    )

    # 4) Call list_topics to send a list_tags WebSocket command and get back
    #    the full tag catalogue from the server.
    #    The return value is: {tag_key: [value, value, ...], ...}
    #    Pass exclude_noisy=False to also include high-cardinality keys like
    #    'timestamp' that are suppressed by default in the API.
    topics: dict[str, list[str]] = monitor.list_topics(
        limit=args.limit,
        exclude_noisy=not args.show_all,
    )

    # 5) Apply optional filters.
    if args.key:
        # Restrict to a single key the user asked for.
        topics = {args.key: topics.get(args.key, [])}

    if args.task_id:
        # Keep only tag keys whose value list contains the requested task ID.
        topics = {k: v for k, v in topics.items() if args.task_id in v}

    # 6) Output.
    if args.as_json:
        print(json.dumps(topics, indent=2))
        return

    if not topics:
        print(
            "No topics found"
            + (" matching the given filters." if (args.key or args.task_id) else ".")
        )
        return

    # Human-readable table: one row per tag key, with all values listed.
    print(f"{'TAG KEY':<30}  COUNT  VALUES")
    print("-" * 88)
    for key in sorted(topics):
        values = topics[key]
        # Print the first value on the same line; subsequent values indented.
        first, *rest = values if values else ["(none)"]
        print(f"{key:<30}  {len(values):>5}  {first}")
        for val in rest:
            print(f"{'':30}         {val}")


if __name__ == "__main__":
    main()
