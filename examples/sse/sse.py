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

"""Stream operation progress updates via Server-Sent Events (SSE).

This example demonstrates how to:

1. Authenticate once with ``Client``.
2. Create a long-running operation that sends periodic updates.
3. Subscribe to operation updates via SSE events.
4. Parse and display each update as it arrives.

The operation runs for a configurable duration (``--sleep`` seconds) and sends
progress updates via Server-Sent Events, which can be monitored in real-time.

Typical usage (local endpoint with API key):

    python examples/sse/sse.py \\
        -U http://127.0.0.1:1081 \\
        --api-key <API_KEY> \\
        --sleep 30

With username/password auth (HTTPS):

    python examples/sse/sse.py \\
        -U https://localhost:8443/hps \\
        -u repadmin \\
        -p repadmin \\
        --sleep 30
"""

import argparse

from ansys.hps.client import Client
from ansys.hps.client.examples import base_parser, client_from_args


def _start_operation(client: Client, sleep_seconds: int, wait_seconds: int = -1) -> str:
    """Start a long-running example operation and return its operation ID.

    Parameters
    ----------
    client : Client
        Authenticated HPS client.
    sleep_seconds : int
        How long the operation should run.
    wait_seconds : int
        Timeout for operation completion. -1 means no timeout.

    Returns
    -------
    str
        The operation ID.

    """
    url = f"{client.url}/jms/api/v1/operations/example"
    params = {"sleep": sleep_seconds, "wait": wait_seconds}

    response = client.session.post(url, params=params)
    response.raise_for_status()
    data = response.json()
    operation_id = data.get("operation_id")

    return operation_id


def _stream_sse_events(
    client: Client,
    operation_id: str,
    timeout_seconds: float = 60.0,
) -> None:
    """Stream operation updates via Server-Sent Events (SSE).

    Parameters
    ----------
    client : Client
        Authenticated HPS client.
    operation_id : str
        The operation ID to monitor.
    timeout_seconds : float
        Request timeout in seconds.

    """
    url = f"{client.url}/jms/api/v1/events"
    # Listen for both updated and completed events
    event_types = "operation:updated,operation:completed"
    params = {"event_types": event_types, "subject": operation_id}

    response = client.session.get(url, params=params, stream=True, timeout=timeout_seconds)
    response.raise_for_status()

    print(f"Monitoring operation {operation_id} via SSE")
    print("-" * 88)

    try:
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            print(line)
            if "operation:completed" in line:
                print("Received 'operation:completed' event. Stopping SSE stream.")
                print("-" * 88)
                break

    except KeyboardInterrupt:
        print("\nInterrupted by user.")

    finally:
        response.close()


def main() -> None:
    parser = argparse.ArgumentParser(parents=[base_parser])
    parser.add_argument(
        "--sleep",
        type=int,
        default=20,
        help="How long the operation should run (in seconds). Default: 20.",
    )
    args = parser.parse_args()

    try:
        # 1) Authenticate with the HPS client
        print("Connect to HPS")
        hps = client_from_args(args)
        print(f"HPS URL: {hps.url}")
        print()

        # 2) Start a long-running example operation
        print(f"Starting operation (sleep={args.sleep}s)...")
        operation_id = _start_operation(hps, sleep_seconds=args.sleep)
        print(f"Operation started with ID: {operation_id}")
        print()

        # 3) Stream and display operation updates via SSE
        _stream_sse_events(hps, operation_id, timeout_seconds=args.sleep + 5.0)

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
