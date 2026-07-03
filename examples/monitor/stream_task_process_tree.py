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

"""Stream process-tree metric snapshots for a task with ``MonitorClient.stream_task_process_tree``.

The evaluator pushes a new process-tree snapshot on a fixed interval while the
task is running.  Each snapshot lists every process in the task's process group
with its PID, parent PID, name, CPU usage, and memory usage.

Usage (local dev with self-signed cert):

    python examples/monitor/stream_task_process_tree.py \\
        --base-url https://localhost:8443/hps \\
        --username repadmin \\
        --password repadmin \\
        --task-id <TASK_ID> \\
        --insecure

Pass ``--tree`` to indent child processes under their parent in each snapshot.
Pass ``--interval 20`` to print a one-line rolling summary every 20 seconds
instead of printing every snapshot in full.  Press Ctrl+C to stop.
"""

from __future__ import annotations

import argparse
import json
import ssl
import time
from datetime import datetime, timezone
from typing import Any

from ansys.hps.client import Client
from ansys.hps.client.monitor.api.monitor_api import MonitorClient


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Stream process-tree metric snapshots for a running task."
    )
    parser.add_argument("--base-url", default="https://localhost:8443/hps")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument(
        "--backlog",
        type=int,
        default=20,
        help="Historical snapshots to request on connect (default: 20).",
    )
    parser.add_argument(
        "--tree",
        action="store_true",
        help="Indent child processes under their parent (uses ppid field).",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=0,
        metavar="SECONDS",
        help=(
            "If >0, accumulate snapshots and print a rolling summary every N seconds "
            "instead of printing each snapshot in full. Default: 0 (print every snapshot)."
        ),
    )
    parser.add_argument(
        "--max-messages",
        type=int,
        default=None,
        help="Maximum snapshots to receive. Omit for unlimited streaming.",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification for local/self-signed endpoints.",
    )
    return parser


def _extract_processes(msg: dict[str, Any]) -> list[dict[str, Any]]:
    """Return a flat process list from a process-tree snapshot message.

    The server embeds the metric payload as a JSON string in the ``message``
    field.  The payload is the *root* process node with nested ``children``::

        {
            "pid": 1234, "ppid": 0, "name": "task_...",
            "cpu_percentage": "92.3",   # string, not float
            "memory_percentage": "4.1", # string, not float
            "state": "running",
            "level": 0,
            "children": [
                {"pid": 5678, "ppid": 1234, "name": "fluent.exe", ...},
                ...
            ]
        }

    This function flattens the nested tree into a plain list (``children``
    key stripped from each node) so callers can iterate without recursion.
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

    if not payload or "pid" not in payload:
        return []

    result: list[dict[str, Any]] = []

    def _flatten(node: dict[str, Any]) -> None:
        result.append({k: v for k, v in node.items() if k != "children"})
        for child in node.get("children", []):
            _flatten(child)

    _flatten(payload)
    return result


def _build_tree(processes: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    """Build a parent → children mapping from the process list."""
    tree: dict[int, list[dict[str, Any]]] = {}
    for proc in processes:
        ppid = proc.get("ppid", 0) or 0
        tree.setdefault(ppid, []).append(proc)
    return tree


def _print_snapshot(
    msg: dict[str, Any],
    processes: list[dict[str, Any]],
    show_tree: bool,
) -> None:
    """Print one process-tree snapshot."""
    ts = (msg.get("time") or msg.get("timestamp") or "")[:19]
    n = len(processes)
    print(f"{ts}  [{n} process{'es' if n != 1 else ''}]")

    if not processes:
        return

    if show_tree:
        children = _build_tree(processes)
        pids = {p.get("pid") for p in processes}
        # Find roots: processes whose ppid is not in the pid set.
        roots = [p for p in processes if (p.get("ppid") or 0) not in pids]
        if not roots:
            roots = processes

        def _walk(proc: dict[str, Any], depth: int) -> None:
            indent = "  " * depth
            pid = proc.get("pid", "?")
            name = proc.get("name", "?")
            cpu_raw = proc.get("cpu_percentage")
            mem_raw = proc.get("memory_percentage")
            cpu = float(cpu_raw) if cpu_raw is not None else None
            mem = float(mem_raw) if mem_raw is not None else None
            cpu_s = f"{cpu:5.1f}%" if cpu is not None else "   n/a"
            mem_s = f"{mem:5.1f}%" if mem is not None else "   n/a"
            status = proc.get("state", "")
            print(f"  {indent}{pid:<8} {name:<24} cpu {cpu_s}  mem {mem_s}  {status}")
            for child in children.get(pid, []):
                _walk(child, depth + 1)

        print(f"  {'pid':<8} {'name':<24} {'cpu':>9}  {'mem':>9}  status")
        print("  " + "-" * 64)
        for root in roots:
            _walk(root, 0)
    else:
        print(f"  {'pid':<8} {'name':<24} {'cpu':>9}  {'mem':>9}  status")
        print("  " + "-" * 64)
        for proc in sorted(processes, key=lambda p: -float(p.get("cpu_percentage") or 0)):
            pid = proc.get("pid", "?")
            name = proc.get("name", "?")
            cpu_raw = proc.get("cpu_percentage")
            mem_raw = proc.get("memory_percentage")
            cpu = float(cpu_raw) if cpu_raw is not None else None
            mem = float(mem_raw) if mem_raw is not None else None
            cpu_s = f"{cpu:5.1f}%" if cpu is not None else "   n/a"
            mem_s = f"{mem:5.1f}%" if mem is not None else "   n/a"
            status = proc.get("state", "")
            print(f"  {pid:<8} {name:<24} cpu {cpu_s}  mem {mem_s}  {status}")

    print()


def _print_summary(
    window_end: str,
    snapshot_count: int,
    proc_counts: list[int],
    top_cpu_vals: list[tuple[float, str]],
) -> None:
    """Print a one-line rolling window summary."""
    if proc_counts:
        min_procs = min(proc_counts)
        max_procs = max(proc_counts)
        last_procs = proc_counts[-1]
        procs_s = f"{last_procs} (min {min_procs} max {max_procs})"
    else:
        procs_s = "n/a"

    if top_cpu_vals:
        best_cpu, best_name = max(top_cpu_vals, key=lambda x: x[0])
        top_s = f"{best_name} @ {best_cpu:.1f}%"
    else:
        top_s = "n/a"

    print(f"{window_end}   snapshots {snapshot_count:>4}   procs {procs_s:<24}   top cpu {top_s}")


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
    monitor = MonitorClient(
        base_url=args.base_url,
        token=hps.access_token,
        client=hps,
        ws_connection_options=ws_options,
        timeout_seconds=30.0,
    )

    print(f"Streaming process-tree snapshots for task {args.task_id}")
    print("Press Ctrl+C to stop")

    use_summary = args.interval > 0
    if use_summary:
        print(f"Rolling summary every {args.interval}s")
    elif args.tree:
        print("Showing tree view (child processes indented under parent)")

    print("-" * 88)

    snapshot_count = 0
    proc_counts: list[int] = []
    top_cpu_vals: list[tuple[float, str]] = []
    window_start = time.monotonic()

    try:
        # 4) stream_task_process_tree subscribes to process_tree metric messages
        #    for the given task_id.  Each yielded dict is one snapshot pushed by
        #    the evaluator on its reporting interval.
        for msg in monitor.stream_task_process_tree(
            task_id=args.task_id,
            backlog=args.backlog,
            max_messages=args.max_messages,
        ):
            processes = _extract_processes(msg)
            snapshot_count += 1

            if use_summary:
                proc_counts.append(len(processes))
                if processes:
                    top = max(processes, key=lambda p: float(p.get("cpu_percentage") or 0))
                    cpu_raw = top.get("cpu_percentage")
                    cpu = float(cpu_raw) if cpu_raw is not None else None
                    name = top.get("name", "?")
                    if cpu is not None:
                        top_cpu_vals.append((cpu, name))

                now = time.monotonic()
                if now - window_start >= args.interval:
                    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
                    _print_summary(ts, snapshot_count, proc_counts, top_cpu_vals)
                    snapshot_count = 0
                    proc_counts = []
                    top_cpu_vals = []
                    window_start = now
            else:
                _print_snapshot(msg, processes, show_tree=args.tree)

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        if use_summary and (proc_counts or snapshot_count):
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
            _print_summary(ts, snapshot_count, proc_counts, top_cpu_vals)


if __name__ == "__main__":
    main()
