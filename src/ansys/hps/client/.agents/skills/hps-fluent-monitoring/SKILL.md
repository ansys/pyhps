---
name: hps-fluent-monitoring
description: Live monitoring of Ansys Fluent jobs running on HPS — which file to tail, residual regex, column mapping, whitespace gotcha, and a complete working script from a real nozzle run. Always load hps-solver-monitoring alongside this for shared timeout/reset/token patterns.
---

# HPS Fluent Monitoring

Load `hps-solver-monitoring` first for timeout, reset, and token patterns shared across all solvers. This file covers Fluent-specific output format and the known gotchas.

## Which file to tail

Fluent writes iteration output to `console_output.txt`. Pass this as the `file_path` filter to `stream_task_logs` — the filter is applied server-side.

```python
for msg in monitor.stream_task_logs(
    task_id=task_id,
    file_path="console_output.txt",
    backlog=2000,
):
```

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

## Debugging: log the first N messages

If residuals are not matching, add this to print the raw incoming messages before applying the regex:

```python
DEBUG_MSGS = 20
msg_count = 0

for msg in monitor.stream_task_logs(task_id=task_id, backlog=2000):
    msg_count += 1
    if msg_count <= DEBUG_MSGS:
        text = msg.get("message", "")
        fp = msg.get("file_path", "?")
        ct = msg.get("client_type", "?")
        print(f"MSG:{msg_count} file={fp!r} type={ct!r} text={text[:80]!r}", flush=True)
```

## Iteration timing

Typical Fluent iteration wall time: 30–120 s. There are silent stretches between iterations (solver writing, mesh adaption, etc.). This is why `timeout_seconds=300.0` is required in `MonitorClient`.

## Duplicate messages from multiple streams

If `backlog` catches historical messages, the same iteration line can arrive multiple times (once from backlog, once from live). Deduplicate by checking if the iteration number already exists:

```python
seen_iters = set()

m = RESIDUAL_RE.match(text)
if m:
    it = int(m.group(1))
    if it not in seen_iters:
        seen_iters.add(it)
        residuals.append(row)
```

## Complete working script (nozzle example, validated 2026-07-07)

This script was used to successfully monitor a 100-iteration Fluent nozzle job on HPS. Copy, update the constants at the top, and run from the project root with `python script.py`.

```python
#!/usr/bin/env python
"""Reset Fluent job on HPS and stream residuals into a live convergence plot HTML."""
import sys, json, math, time, re, ssl, traceback
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
    if job.eval_status in ("evaluated", "failed", "aborted"):
        job.eval_status = "pending"
        project_api.update_jobs([job])
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

    # MonitorClient — timeout MUST be >> iteration wall time
    monitor = MonitorClient(
        client=client,
        ws_connection_options={"sslopt": {"cert_reqs": ssl.CERT_NONE}},
        timeout_seconds=300.0,
    )

    residuals = []
    seen_iters = set()
    last_check = time.time()

    for msg in monitor.stream_task_logs(task_id=task_id, backlog=2000):
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

        # Periodic done-check
        now = time.time()
        if now - last_check > 15:
            last_check = now
            tasks = project_api.get_tasks(job_id=JOB_ID)
            cur = next((t for t in tasks if t.id == task_id), None)
            if cur and cur.eval_status in ("evaluated", "failed", "aborted"):
                print(f"DONE:{cur.eval_status}")
                return

    # Final cleanup after stream ends
    tasks = project_api.get_tasks(job_id=JOB_ID)
    cur = next((t for t in tasks if t.id == task_id), None)
    print(f"DONE:{cur.eval_status if cur else 'unknown'}")


if __name__ == "__main__":
    main()
```

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
