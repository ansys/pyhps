"""Annotated example: stream host CPU/memory metrics with MonitorClient.stream_task_host_resources.

``stream_task_host_resources`` automatically resolves the evaluator assigned to
a task (via JMS and RMS) and subscribes to ``host_resources`` metric messages
for that evaluator.  Each message contains a snapshot of the host's CPU and
memory utilisation.

Usage (local dev with self-signed cert):

    python examples/monitor/stream_task_host_resources.py \\
        --base-url https://localhost:8443/hps \\
        --username repadmin \\
        --password repadmin \\
        --task-id <TASK_ID> \\
        --insecure

Pass ``--interval 20`` to print a rolling 20-second summary instead of every
raw message.  Press Ctrl+C to stop.
"""

from __future__ import annotations

import argparse
import json
import ssl
import statistics
import time
from datetime import datetime, timezone
from typing import Any

from ansys.hps.client import Client
from ansys.hps.client.monitor.api.monitor_api import MonitorClient


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Stream host CPU/memory metrics for a running task."
    )
    parser.add_argument("--base-url", default="https://localhost:8443/hps")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--backlog", type=int, default=20,
                        help="Historical metric snapshots to request on connect (default: 20).")
    parser.add_argument(
        "--interval",
        type=int,
        default=0,
        metavar="SECONDS",
        help=(
            "If >0, accumulate samples and print a rolling summary every N seconds "
            "instead of printing each raw message. Default: 0 (print every message)."
        ),
    )
    parser.add_argument(
        "--max-messages",
        type=int,
        default=None,
        help="Maximum metric messages to receive. Omit for unlimited streaming.",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification for local/self-signed endpoints.",
    )
    return parser


def _extract_metrics(msg: dict[str, Any]) -> tuple[float | None, float | None]:
    """Pull CPU usage and memory percent out of a host_resources message.

    The server embeds the metric payload as a JSON string in the ``message``
    field with the shape::

        {
            "cpu": {"usage": 42.4, "per_core": [...]},
            "virtual_memory": {"percent": 88.9, ...},
            ...
        }
    """
    raw = msg.get("message", "")
    if isinstance(raw, str):
        try:
            payload = json.loads(raw)
        except (ValueError, TypeError):
            payload = {}
    elif isinstance(raw, dict):
        payload = raw
    else:
        payload = {}

    try:
        cpu = float(payload["cpu"]["usage"])
    except (KeyError, TypeError, ValueError):
        cpu = None

    try:
        mem = float(payload["virtual_memory"]["percent"])
    except (KeyError, TypeError, ValueError):
        mem = None

    return cpu, mem


def _print_raw(msg: dict[str, Any]) -> None:
    """Print a single host-resources message in a compact tabular form."""
    ts = (msg.get("time") or msg.get("timestamp") or "")[:19]
    cpu, mem = _extract_metrics(msg)
    cpu_s = f"{cpu:6.1f}%" if cpu is not None else "   n/a"
    mem_s = f"{mem:6.1f}%" if mem is not None else "   n/a"
    print(f"{ts}   cpu {cpu_s}   mem {mem_s}")


def _print_summary(
    window_end: str,
    cpu_vals: list[float],
    mem_vals: list[float],
) -> None:
    """Print a one-line rolling window summary."""
    def _fmt(vals: list[float]) -> str:
        if not vals:
            return "  n/a    n/a    n/a    n/a"
        return (
            f"{vals[-1]:6.1f}  "
            f"{min(vals):6.1f}  "
            f"{max(vals):6.1f}  "
            f"{statistics.mean(vals):6.1f}"
        )

    n = max(len(cpu_vals), len(mem_vals))
    print(f"{window_end}   {n:>5}   cpu {_fmt(cpu_vals)}   mem {_fmt(mem_vals)}")


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
    ws_options: dict[str, Any] | None = None
    if args.insecure:
        ws_options = {"sslopt": {"cert_reqs": ssl.CERT_NONE}}

    # 3) Build a MonitorClient that reuses the authenticated client and token.
    #    Passing client=hps allows stream_task_host_resources to resolve the
    #    evaluator via JMS/RMS without creating a second login.
    monitor = MonitorClient(
        base_url=args.base_url,
        token=hps.access_token,
        client=hps,
        ws_connection_options=ws_options,
        timeout_seconds=30.0,
    )

    print(f"Streaming host resources for task {args.task_id}")
    print("(resolving evaluator via JMS/RMS...)")

    use_summary = args.interval > 0

    if use_summary:
        print(f"Reporting every {args.interval}s")
        print(
            f"{'time_utc':<19}   {'n':>5}   "
            f"{'cpu_last':>8}  {'cpu_min':>7}  {'cpu_max':>7}  {'cpu_avg':>7}   "
            f"{'mem_last':>8}  {'mem_min':>7}  {'mem_max':>7}  {'mem_avg':>7}"
        )
    else:
        print("Press Ctrl+C to stop")
        print(f"{'time':<19}   {'cpu':>9}   {'mem':>9}")

    print("-" * 88)

    cpu_vals: list[float] = []
    mem_vals: list[float] = []
    window_start = time.monotonic()

    try:
        # 4) stream_task_host_resources resolves the evaluator and subscribes to
        #    the host_resources metric statistic for it.  Each yielded dict is one
        #    metric snapshot pushed by the server.
        for msg in monitor.stream_task_host_resources(
            task_id=args.task_id,
            backlog=args.backlog,
            max_messages=args.max_messages,
        ):
            cpu, mem = _extract_metrics(msg)

            if use_summary:
                # Accumulate into rolling window.
                if cpu is not None:
                    cpu_vals.append(cpu)
                if mem is not None:
                    mem_vals.append(mem)

                now = time.monotonic()
                if now - window_start >= args.interval:
                    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
                    _print_summary(ts, cpu_vals, mem_vals)
                    cpu_vals = []
                    mem_vals = []
                    window_start = now
            else:
                _print_raw(msg)

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        if use_summary and (cpu_vals or mem_vals):
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
            _print_summary(ts, cpu_vals, mem_vals)


if __name__ == "__main__":
    main()
