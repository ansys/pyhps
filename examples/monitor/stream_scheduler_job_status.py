"""Annotated example: stream scheduler job status with MonitorClient.stream_scheduler_job_status.

``stream_scheduler_job_status`` subscribes to ``scaler_instances`` metric messages
emitted by the HPS autoscaling service (``ansys.rep.scaling``) for a specific task
definition.  Each message is a status update from the underlying job scheduler
(e.g. Slurm or LSF) and contains instance-count information for the scaler.

Usage (local dev with self-signed cert):

    python examples/monitor/stream_scheduler_job_status.py \\
        --base-url https://localhost:8443/hps \\
        --username repadmin \\
        --password repadmin \\
        --task-definition-id <TASK_DEFINITION_ID> \\
        --insecure

Press Ctrl+C to stop streaming.
"""

from __future__ import annotations

import argparse
import json
import ssl
from typing import Any

from ansys.hps.client import Client
from ansys.hps.client.monitor.api.monitor_api import MonitorClient


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Stream scheduler job status metrics for a task definition."
    )
    parser.add_argument("--base-url", default="https://localhost:8443/hps")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument(
        "--task-definition-id",
        required=True,
        help="Task definition ID to monitor scheduler job status for.",
    )
    parser.add_argument(
        "--backlog",
        type=int,
        default=20,
        help="Historical metric messages to request on connect (default: 20).",
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


def _parse_payload(msg: dict[str, Any]) -> dict[str, Any]:
    """Extract the inner JSON payload from the ``message`` field.

    Each ``scaler_instances`` metric message embeds the scheduler instance
    record as a JSON string in the ``message`` field.  The shape is::

        {
            "state": "SUBMITTED" | "RUNNING" | "COMPLETED" | "FAILED",
            "orchestrator_id": "14072143",
            "instance_id": "e2da1296-...",
            "scaler_type": "slurm",
            "resource_name": "oc-slurm",
            "created_on": "2026-06-29T14:26:10...",
            "started_on": "2026-06-29T18:26:18..." | null,
            "keep": true,
            "exit_state_checked": false,
            "messages": [...],
            ...
        }
    """
    raw = msg.get("message", "")
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except (ValueError, TypeError):
            return {}
    return raw if isinstance(raw, dict) else {}


def _print_status(msg: dict[str, Any]) -> None:
    """Print a single scaler_instances message in a compact tabular form."""
    ts = (msg.get("time") or msg.get("timestamp") or "")[:19]
    payload = _parse_payload(msg)
    state = payload.get("state") or "unknown"
    scheduler = payload.get("scaler_type") or payload.get("resource_name") or "unknown"
    job_id = payload.get("orchestrator_id") or "n/a"
    started = (payload.get("started_on") or "")[:19] or "not started"
    print(f"{ts}   {scheduler:<10}   {state:<12}   job={job_id:<12}   started={started}")


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

    # 3) Build a MonitorClient that reuses the authenticated token.
    monitor = MonitorClient(
        base_url=args.base_url,
        token=hps.access_token,
        ws_connection_options=ws_options,
        timeout_seconds=30.0,
    )

    print(f"Streaming scheduler job status for task definition {args.task_definition_id}")
    print("Press Ctrl+C to stop")
    print(f"{'time':<19}   {'scheduler':<10}   {'state':<12}   {'job id':<16}   {'started'}")
    print("-" * 80)

    try:
        # 4) stream_scheduler_job_status subscribes to scaler_instances metric
        #    messages for the given task definition.  Each yielded dict is one
        #    status update from the job scheduler (e.g. Slurm or LSF).
        for msg in monitor.stream_scheduler_job_status(
            task_definition_id=args.task_definition_id,
            backlog=args.backlog,
            max_messages=args.max_messages,
        ):
            _print_status(msg)

    except KeyboardInterrupt:
        print("\nInterrupted by user.")


if __name__ == "__main__":
    main()
