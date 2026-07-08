---
name: hps-fluent-monitoring
description: Live monitoring of Ansys Fluent jobs running on HPS — which file to tail, residual regex, column mapping, whitespace gotcha, and a complete working script from a real nozzle run. Always load hps-solver-monitoring alongside this for shared timeout/reset/token patterns.
---

# HPS Fluent Monitoring

Load `hps-solver-monitoring` first for timeout, reset, and token patterns shared across all solvers. This file covers Fluent-specific output format and the known gotchas.

## Which file to tail

Fluent writes iteration output to `console_output.txt`. You can pass this as a server-side `file_path` filter on `stream_task_logs` to reduce WebSocket traffic:

```python
for msg in monitor.stream_task_logs(
    task_id=task_id,
    file_path="console_output.txt",
    backlog=2000,
):
```

**Critical**: `msg.get("file_path")` is `None` on many HPS server versions — do NOT use it for client-side dispatch. The server-side `file_path` parameter on `stream_task_logs` works (it filters what the server sends), but the `file_path` field inside the arriving `MonitorMessage` dicts is often absent. Always filter by regex/content, not by checking `msg.get("file_path")`.

Other files present in a typical Fluent task: `.trn` transcript, `*.out`, case/data files. These are not useful for residual monitoring.

## Residual line format

Fluent writes one line per iteration in this format (columns separated by whitespace):

```
<iter>  <continuity>  <x-velocity>  <y-velocity>  <z-velocity>  <energy>  [<vol-mon-1>  <vol-mon-2>  <surf-mon-1>  <surf-mon-2>]  <time/iter>
```

Example:
```
 42  6.4715e-01  7.5243e-01  3.1877e-01  3.1877e-01  1.0000e+00  1.2e-03  3.4e-03  2.1  3.8  0:01:32  58 more iterations
```

The number of monitor columns depends on what was set up in the case. Monitor columns are optional — they may be absent.

## Critical: leading whitespace stripped by monitor service

The HPS file-tail monitor service strips leading whitespace before sending lines. The raw Fluent log has a leading space before each iteration number (` 42  6.47...`), but the message received via WebSocket has that space removed (`42  6.47...`).

**Use `^\s*` (zero or more), not `^\s+` (one or more), in the regex:**

```python
RESIDUAL_RE = re.compile(
    r"^\s*(\d+)"
    r"\s+([\d.e+\-]+)\s+([\d.e+\-]+)\s+([\d.e+\-]+)\s+([\d.e+\-]+)\s+([\d.e+\-]+)"
    r"(?:\s+([\d.e+\-]+)\s+([\d.e+\-]+)\s+([\d.e+\-]+)\s+([\d.e+\-]+))?"
)
RES_KEYS = ["continuity", "x-velocity", "y-velocity", "z-velocity", "energy"]
MON_KEYS = ["vol-mon-1", "vol-mon-2", "surf-mon-1", "surf-mon-2"]
```

## Debugging: dump raw messages first

If residuals are not matching, run a raw diagnostic before touching the regex. This exposes field names, column counts, and duplicate behaviour in one shot:

```python
# Run this as a standalone script first — exits after 30 messages
for msg in monitor.stream_task_logs(task_id=task_id, backlog=30, max_messages=30):
    fp   = msg.get("file_path", "<none>")   # often None — do not rely on this
    text = msg.get("message", "")[:100]
    print(f"file={fp!r:30s}  msg={text!r}", flush=True)
```

Common findings:
- `file_path` is `None` → do not filter by filename, use regex
- The same iteration line appears 2× back-to-back → always deduplicate with `seen_iters`
- Column count differs from the regex → adjust `RESIDUAL_RE` to match actual columns
- Non-residual lines (headers, warnings, status) appear → regex filters them out automatically

## Iteration timing

Typical Fluent iteration wall time: 30–120 s. There are silent stretches between iterations (solver writing, mesh adaption, etc.). This is why `timeout_seconds=300.0` is required in `MonitorClient`.

## Duplicate messages — always deduplicate

The same iteration line arrives **two or more times** from the stream — this happens even in persistent (non-reconnecting) streams, not only when replaying backlog. `seen_iters` deduplication is not optional. Two strategies:

**Strategy A — deduplicate by iteration number** (for one-shot catch-up):

```python
seen_iters = set()

m = RESIDUAL_RE.match(text)
if m:
    it = int(m.group(1))
    if it not in seen_iters:
        seen_iters.add(it)
        residuals.append(row)
```

**Strategy B — use `tail_only=True` + `since`** (for reconnecting poll loops, e.g. live plots):

```python
last_ts = None

while True:
    for msg in monitor.stream_task_logs(
        task_id=task_id,
        file_path="console_output.txt",
        tail_only=True,    # no history replay on each reconnect
        since=last_ts,     # skip messages already processed
        max_messages=1000,
    ):
        text = msg.get("message", "").strip()
        m = RESIDUAL_RE.match(text)
        if m:
            residuals.append(...)
        ts = msg.get("time") or msg.get("timestamp")
        if ts:
            last_ts = ts
    time.sleep(15)
```

Strategy B eliminates the replay problem entirely — no deduplication needed. Without `tail_only=True`, each reconnect replays `backlog` lines from the start of the run, which on a long job (50k+ lines) means thousands of stale messages before any live data arrives.

## Complete working script (nozzle example, validated 2026-07-07)

This script was used to successfully monitor a 100-iteration Fluent nozzle job on HPS. Copy, update the constants at the top, and run from the project root with `python script.py`.

Uses `stream_task_all` for one-loop monitoring of residuals (from `console_output.txt`), process tree, and host resources.

```python
#!/usr/bin/env python
"""Reset Fluent job on HPS and stream residuals into a live convergence plot HTML."""
import json, time, re, ssl
from pathlib import Path

HPS_URL    = "https://localhost:8443/hps"
PROJECT_ID = "your-project-id"
JOB_ID     = "your-job-id"
HTML_OUT   = Path("convergence_plot.html")
JSON_OUT   = Path("residuals.json")

RESIDUAL_RE = re.compile(
    r"^\s*(\d+)"
    r"\s+([\d.e+\-]+)\s+([\d.e+\-]+)\s+([\d.e+\-]+)\s+([\d.e+\-]+)\s+([\d.e+\-]+)"
    r"(?:\s+([\d.e+\-]+)\s+([\d.e+\-]+)\s+([\d.e+\-]+)\s+([\d.e+\-]+))?"
)
RES_KEYS = ["continuity", "x-velocity", "y-velocity", "z-velocity", "energy"]
MON_KEYS = ["vol-mon-1", "vol-mon-2", "surf-mon-1", "surf-mon-2"]


def main():
    from ansys.hps.client.auth.api.oidc_login import refresh_tokens, browser_login, save_tokens
    from ansys.hps.client import Client
    from ansys.hps.client.jms import ProjectApi
    from ansys.hps.client.monitor import MonitorClient

    # Auth — refresh first, fall back to browser PKCE login
    tokens = refresh_tokens(hps_url=HPS_URL, storage="keyring", verify_ssl=False)
    if not tokens:
        tokens = browser_login(HPS_URL, verify_ssl=False)
        save_tokens(tokens, HPS_URL, storage="keyring")

    client = Client(
        url=HPS_URL,
        access_token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token"),  # enables auto-refresh; without this, 25-min TTL kills long runs
        verify=False,
    )
    project_api = ProjectApi(client, PROJECT_ID)

    # Record existing task IDs before reset
    old_ids = {t.id for t in project_api.get_tasks(job_id=JOB_ID)}

    # Conditional reset
    jobs = project_api.get_jobs(id=JOB_ID)
    job = jobs[0]
    was_reset = False
    if job.eval_status in ("evaluated", "failed", "aborted"):
        job.eval_status = "pending"
        project_api.update_jobs([job])
        was_reset = True
        print("JOB_RESET")
    elif job.eval_status == "running":
        print("JOB_ALREADY_RUNNING: attaching")
    elif job.eval_status == "pending":
        print("JOB_PENDING: waiting for evaluator")

    # Poll for running task
    task_id = None
    deadline = time.time() + 600
    while time.time() < deadline:
        tasks = project_api.get_tasks(job_id=JOB_ID)
        running = [t for t in tasks if t.eval_status == "running"]
        if running:
            fresh = [t for t in running if t.id not in old_ids]
            task_id = (fresh or running)[0].id
            print(f"TASK_RUNNING:{task_id}")
            break
        time.sleep(2)

    if not task_id:
        print("ERROR: Timeout waiting for running task")
        return

    # MonitorClient — timeout MUST be >> iteration wall time (Fluent iterations: 30-120 s)
    monitor = MonitorClient(
        client=client,
        ws_connection_options={"sslopt": {"cert_reqs": ssl.CERT_NONE}},
        timeout_seconds=300.0,
    )

    residuals = []
    seen_iters = set()

    # stream_task_all: one loop for log + process_tree + host_resources.
    # job_id terminates the stream automatically when job reaches a terminal status.
    # tail_only=was_reset skips old-run history when task ID is recycled after reset.
    for event in monitor.stream_task_all(
        task_id=task_id,
        job_id=JOB_ID,
        project_id=PROJECT_ID,
        tail_only=was_reset,
        backlog=2000,
    ):
        kind = event["kind"]
        msg  = event["msg"]

        if kind == "log":
            # msg.get("file_path") is None on many server versions — do NOT use it
            # for dispatch. Filter by regex only: RESIDUAL_RE is specific enough.
            text = msg.get("message", "")
            m = RESIDUAL_RE.match(text)
            if m:
                it = int(m.group(1))
                if it not in seen_iters:
                    seen_iters.add(it)
                    row = {"iter": it}
                    for i, key in enumerate(RES_KEYS):
                        row[key] = float(m.group(i + 2))
                    if m.group(7) is not None:
                        for i, key in enumerate(MON_KEYS):
                            row[key] = float(m.group(i + 7))
                    residuals.append(row)
                    JSON_OUT.write_text(json.dumps(residuals))
                    # write convergence_plot.html here (see make_html in full script)
                    print(f"ITER:{it}")

        elif kind == "process_tree":
            payload = msg.parsed_message  # auto-decoded from JSON string
            if payload and isinstance(payload, dict) and "pid" in payload:
                # payload is the root process node; recurse for children
                pass  # handle_proc_snapshot(payload)

        elif kind == "host_resources":
            payload = msg.parsed_message or {}
            cpu = payload.get("cpu", {}).get("usage")
            mem = payload.get("virtual_memory", {}).get("percent")
            if cpu is not None:
                print(f"HOST: cpu={float(cpu):.1f}%  mem={float(mem):.1f}%", flush=True)

    # Stream has exited — job is in a terminal state
    jobs = project_api.get_jobs(id=JOB_ID)
    status = jobs[0].eval_status if jobs else "unknown"
    print(f"DONE:{status}")


if __name__ == "__main__":
    main()
```

**Logs-only variant** (if you don't need proc tree or host metrics):

```python
for msg in monitor.stream_task_logs(
    task_id=task_id,
    file_path="console_output.txt",   # server-side filter; reduces WebSocket traffic
    job_id=JOB_ID,
    project_id=PROJECT_ID,
    tail_only=was_reset,
    backlog=2000,
):
    text = msg.get("message", "")
    ...
```

Use `stream_task_logs` with `file_path` when you only care about one file — the server-side filter prevents all other tailed files from being sent over the WebSocket. Note: this server-side `file_path` parameter works correctly; it's the `file_path` field *inside* the arriving messages that is unreliable (often `None`).

## Live HTML convergence plot (local, auto-refresh)

Write an HTML file with `<meta http-equiv="refresh" content="10">` and open it in a browser. On Windows use `start`:

```python
import subprocess
HTML_OUT = Path("convergence_plot.html")
HTML_OUT.write_text(initial_html_content)
subprocess.Popen(["start", str(HTML_OUT)], shell=True)  # open in default browser
```

The browser auto-refreshes every 10 s while the script rewrites the file each iteration. No server, no WebSockets in the browser — just static HTML with a meta refresh.

Do NOT use the Artifact tool for this — it requires rendering in the Claude environment and does not work for local file watching.
