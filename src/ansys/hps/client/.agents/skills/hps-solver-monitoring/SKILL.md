---
name: hps-solver-monitoring
description: Shared patterns for live monitoring of HPS solver tasks via MonitorClient — timeout config, job reset, stream attachment, token management. Load this alongside a solver-specific skill (hps-fluent-monitoring, hps-mapdl-monitoring, hps-aedt-monitoring).
---

# HPS Solver Monitoring — Shared Patterns

Patterns that apply to any solver running as an HPS task. Load this skill alongside a solver-specific one (e.g. `hps-fluent-monitoring`) which covers file names, regex, and output format.

## Critical: MonitorClient timeout_seconds

`MonitorClient` defaults to `timeout_seconds=10.0`. Internally, `_stream_ws` catches `WebSocketTimeoutException` with a **silent `break`** — the generator returns normally with no error while the task is still running. Solver iterations routinely take 30–120 s each, so the default disconnects between every iteration.

**Always set `timeout_seconds` explicitly:**

```python
import ssl
from ansys.hps.client.monitor import MonitorClient

monitor = MonitorClient(
    client=client,
    ws_connection_options={"sslopt": {"cert_reqs": ssl.CERT_NONE}},  # for self-signed certs
    timeout_seconds=300.0,   # must be >> longest gap between log lines
)
```

## Conditional job reset

Only reset to `pending` if the job has already finished. Resetting a running job interrupts the evaluator mid-solve.

```python
jobs = project_api.get_jobs(id=job_id)
job = jobs[0]

if job.eval_status in ("evaluated", "failed", "aborted"):
    job.eval_status = "pending"
    project_api.update_jobs([job])
    print("JOB_RESET")
elif job.eval_status == "running":
    print("JOB_ALREADY_RUNNING: attaching")
elif job.eval_status == "pending":
    print("JOB_PENDING: waiting for evaluator")
```

## Finding the right task after reset

Record existing task IDs before reset so you can detect the new one. After reset HPS may reuse the same task ID with an incremented trial, or create a new one.

```python
old_ids = {t.id for t in project_api.get_tasks(job_id=job_id)}

# ... reset job ...

# Poll for running task — prefer a brand-new task ID
task_id = None
while True:
    tasks = project_api.get_tasks(job_id=job_id)
    running = [t for t in tasks if t.eval_status == "running"]
    if running:
        fresh = [t for t in running if t.id not in old_ids]
        task = (fresh or running)[0]
        task_id = task.id
        break
    prolog = [t for t in tasks if t.eval_status == "prolog"]
    if prolog:
        pass  # evaluator picked up job, will transition to running soon
    time.sleep(2)
```

## Backlog for mid-run attachment

If you attach after the task has been running for a while, `backlog=100` (the default) may not reach far enough back in the log. Use `backlog=2000` to catch up on earlier output.

**Critical**: use `tail_only=True` after a fresh job reset. If the task ID is reused across runs (HPS increments `trial_number` on the same task), the old run's messages are still in the backlog. With `backlog=2000` they replay immediately, filling `seen_iters` with ITER:1-100, which then silently blocks all live iterations from the new run.

```python
# was_reset = True when job.eval_status was evaluated/failed/aborted before reset
for msg in monitor.stream_task_logs(task_id=task_id, tail_only=was_reset, backlog=2000):
    ...
```

`tail_only=True` sends `backlog=0` in the subscribe command — the server replays nothing, only live messages arrive.

## Reconnect loop without history replay (tail_only + since)

For polling/plot-refresh loops that reconnect every N seconds, use `tail_only=True` + `since` to avoid replaying the full log history on every reconnect:

```python
last_ts = None  # ISO 8601 string of last message timestamp seen

while True:
    for msg in monitor.stream_task_logs(
        task_id=task_id,
        file_path="console_output.txt",
        tail_only=True,      # no history replay on connect
        since=last_ts,       # skip messages at or before last seen timestamp
        max_messages=1000,
    ):
        process(msg)
        ts = msg.get("time") or msg.get("timestamp")
        if ts:
            last_ts = ts

    time.sleep(15)
```

Without `tail_only=True`, each reconnect replays `backlog` messages from the beginning of the run. On a job that has been running for hours with 50k log lines, `backlog=10000` means 10k stale messages are delivered before any live data — the live-plot use case experienced this as timesteps going backward.

`since` is a client-side ISO 8601 string filter: any message whose `time` or `timestamp` field is `<=` *since* is silently skipped. Messages with no timestamp are always yielded. The two parameters compose: `tail_only=True` prevents server backlog, `since` catches the edge case where `backlog=0` still replays a message from the exact connect timestamp.

## Done detection — pass job_id to auto-terminate the stream

Pass `job_id` to any stream method and the stream exits automatically once the job reaches a terminal status (`evaluated`, `failed`, `aborted`). A background daemon thread polls JMS every 5 s — no manual threading required:

```python
for msg in monitor.stream_task_logs(
    task_id=task_id,
    job_id=job_id,
    tail_only=True,         # no history replay
):
    process_log_message(msg)
# loop ends automatically when job finishes
```

The same `job_id` parameter works on all three streaming methods:

```python
for snap in proc_mon.stream_task_process_tree(task_id=task_id, job_id=job_id):
    handle_proc_snapshot(snap)

for snap in host_mon.stream_task_host_resources(task_id=task_id, job_id=job_id):
    handle_host_snapshot(snap)
```

The stream terminates within ~5 s of the job status changing. The WebSocket recv timeout is capped at 5 s when `job_id` is set, so done detection is not blocked by a long `timeout_seconds`.

**If you don't have `project_id` handy**, omit it — the client infers it automatically from a small number of task-log messages. Pass it explicitly to skip that round-trip:

```python
for msg in monitor.stream_task_logs(
    task_id=task_id,
    job_id=job_id,
    project_id=project_id,  # optional; avoids an auto-resolve round-trip
):
    ...
```

## Token TTL for long-running jobs

`browser_login` access tokens expire in ~1500 s (25 min). A 100-iteration solver job can take 60–90 min. **Always pass `refresh_token` to `Client`** so it can auto-refresh using `auto_refresh_token=True` (the default).

```python
from ansys.hps.client.auth.api.oidc_login import refresh_tokens, browser_login, save_tokens

tokens = refresh_tokens(hps_url=HPS_URL, storage="keyring", verify_ssl=False)
if not tokens:
    tokens = browser_login(HPS_URL, verify_ssl=False)
    save_tokens(tokens, HPS_URL, storage="keyring")

# CRITICAL: pass refresh_token so Client auto-refreshes during long runs.
# Without it, get_tasks() raises HPSError after ~25 min.
client = Client(
    url=HPS_URL,
    access_token=tokens["access_token"],
    refresh_token=tokens.get("refresh_token"),
    verify=False,
)
```

If you construct `Client` with only `access_token` (no `refresh_token`), the internal `_auto_refresh_token` hook will raise `HPSError: No refresh token available` once the access token expires — even though `auto_refresh_token=True` is set.

## Process tree monitoring

`MonitorClient.stream_task_process_tree` streams process snapshots as WebSocket messages. The process data is **not** at the top level of the message dict — it is a **JSON string** stored in `msg["message"]`, where the string is a single root process node with nested `children`.

Use `msg.parsed_message` to decode the JSON string automatically — no manual `json.loads()` needed:

```python
import threading, ssl
from ansys.hps.client.monitor import MonitorClient

def _extract_processes(msg):
    """Parse process tree from msg.parsed_message (auto-decoded from JSON string)."""
    payload = msg.parsed_message
    if not isinstance(payload, dict) or "pid" not in payload:
        return []
    result = []
    def _flatten(node):
        result.append({k: v for k, v in node.items() if k != "children"})
        for child in node.get("children", []):
            _flatten(child)
    _flatten(payload)
    return result

def print_proc_snapshot(msg):
    processes = _extract_processes(msg)
    ts = (msg.get("time") or msg.get("timestamp") or "")[:19]
    print(f"PROC_SNAP: {ts}  [{len(processes)} processes]", flush=True)
    if not processes:
        return
    pids = {p.get("pid") for p in processes}
    children = {}
    for p in processes:
        ppid = p.get("ppid", 0) or 0
        children.setdefault(ppid, []).append(p)
    roots = [p for p in processes if (p.get("ppid") or 0) not in pids] or processes
    print(f"  {'pid':<8} {'name':<28} {'cpu':>7}  {'mem':>7}  status", flush=True)
    print("  " + "-" * 60, flush=True)
    def walk(p, depth):
        indent = "  " * depth
        pid = p.get("pid", "?")
        cpu = p.get("cpu_percentage")
        mem = p.get("memory_percentage")
        cpu_s = f"{float(cpu):5.1f}%" if cpu is not None else "   n/a"
        mem_s = f"{float(mem):5.1f}%" if mem is not None else "   n/a"
        print(f"  {indent}{pid:<8} {p.get('name','?'):<28} {cpu_s}  {mem_s}  {p.get('state','')}", flush=True)
        for child in children.get(pid, []):
            walk(child, depth + 1)
    for root in roots:
        walk(root, 0)

# Use a separate MonitorClient for process tree — it must not share the log WebSocket.
# timeout_seconds=60 is enough since snapshots arrive every ~4-10 s.
proc_monitor = MonitorClient(
    client=client,
    ws_connection_options={"sslopt": {"cert_reqs": ssl.CERT_NONE}},
    timeout_seconds=60.0,
)

def stream_proc_tree():
    try:
        for snap in proc_monitor.stream_task_process_tree(task_id=task_id, backlog=1):
            if done_event.is_set():
                return
            print_proc_snapshot(snap)
    except Exception as exc:
        print(f"PROC_ERROR:{exc}", flush=True)

threading.Thread(target=stream_proc_tree, daemon=True).start()
```

**Key pitfalls**:
- `msg.get("processes", [])` always returns `[]` — that key does not exist. Use `msg.parsed_message` to get the root node dict.
- `msg.get("message")` returns a raw JSON *string* for metric messages — never treat it as a dict directly. Use `msg.parsed_message` instead.
- `cpu_percentage` and `memory_percentage` are **strings**, not floats — cast with `float()` before arithmetic.
- Root node has `children` list — must recurse to flatten; top-level processes are NOT a flat list.

## Host CPU/memory monitoring

`MonitorClient.stream_task_host_resources` streams host-level CPU and memory snapshots. Same message pattern as process tree — `msg["message"]` is a JSON string. Use `msg.parsed_message` to decode it automatically.

```python
def _extract_host_metrics(msg):
    """msg.parsed_message decodes the JSON string in msg["message"] automatically."""
    payload = msg.parsed_message or {}
    try:
        cpu = float(payload["cpu"]["usage"])
    except (KeyError, TypeError, ValueError):
        cpu = None
    try:
        mem = float(payload["virtual_memory"]["percent"])
    except (KeyError, TypeError, ValueError):
        mem = None
    return cpu, mem

# Requires project_id (unlike process tree which only needs task_id).
# Use a separate MonitorClient; snapshots arrive every ~5 s so timeout_seconds=60 is ample.
host_monitor = MonitorClient(
    client=client,
    ws_connection_options={"sslopt": {"cert_reqs": ssl.CERT_NONE}},
    timeout_seconds=60.0,
)

def stream_host_resources():
    try:
        for snap in host_monitor.stream_task_host_resources(
            task_id=task_id,
            project_id=project_id,
            backlog=5,
        ):
            if done_event.is_set():
                return
            cpu, mem = _extract_host_metrics(snap)
            ts = (snap.get("time") or snap.get("timestamp") or "")[:19]
            print(f"HOST: {ts}  cpu {cpu:5.1f}%  mem {mem:5.1f}%", flush=True)
    except Exception as exc:
        print(f"HOST_ERROR:{exc}", flush=True)

threading.Thread(target=stream_host_resources, daemon=True).start()
```

**Key difference from process tree**: `stream_task_host_resources` needs to know which evaluator host is running the task, resolved via JMS/RMS using `project_id`. Pass `project_id` explicitly when you have it; omit it and the client auto-resolves it from a small number of task-log messages:

```python
# Both forms work:
for snap in host_monitor.stream_task_host_resources(task_id=task_id, project_id=project_id):
    ...
for snap in host_monitor.stream_task_host_resources(task_id=task_id):   # auto-resolves project_id
    ...
```

## stream_task_all — one loop for everything

`stream_task_all` opens log, process-tree, and host-resource streams on background threads and multiplexes them into a single generator.  No manual thread management needed:

```python
for event in monitor.stream_task_all(
    task_id=task_id,
    job_id=job_id,           # exits automatically when job finishes
    project_id=project_id,   # optional — auto-resolved if omitted
    tail_only=True,
):
    kind = event["kind"]   # "log" | "process_tree" | "host_resources"
    msg  = event["msg"]    # MonitorMessage

    if kind == "log":
        text = msg.get("message", "")
        # DO NOT dispatch by msg.get("file_path") — that field is None on many
        # server versions. Use content-based dispatch (regex) instead.
        if RESIDUAL_RE.match(text):
            parse_residual(text)
        elif ERROR_RE.search(text):
            check_for_errors(text)

    elif kind == "process_tree":
        processes = _extract_processes(msg)  # uses msg.parsed_message

    elif kind == "host_resources":
        cpu, mem = _extract_host_metrics(msg)
```

**`file_path` is not reliable for dispatch** — `msg.get("file_path")` returns `None` on many HPS server versions even when multiple files are being tailed simultaneously.  Always use content-based dispatch (regex match on `msg.get("message")`) instead of filename dispatch.

**Duplicate log messages are normal** — the same line can arrive two or more times from the same stream.  Always deduplicate by iteration number or another stable key.  `seen_iters = set()` is not optional.

Use `stream_task_all` when you want everything in one place.  Use the individual `stream_task_logs`, `stream_task_process_tree`, `stream_task_host_resources` when you need fine-grained control (e.g., different backlogs per stream, or only one stream type).

## First-run diagnostic pattern

Before writing a full monitoring script, run a raw message dump to understand what the server actually sends.  This avoids wasting time on wrong field names or missing data:

```python
# diag.py — stream 30 raw log messages and print everything
for msg in monitor.stream_task_logs(task_id=task_id, backlog=30, max_messages=30):
    fp   = msg.get("file_path", "<none>")
    text = msg.get("message", "")[:100]
    print(f"file={fp!r:30s}  msg={text!r}", flush=True)
```

Run this first.  It shows:
- Whether `file_path` is populated (often it is not)
- The exact format of residual/metric lines (column count, separator, scientific notation format)
- Whether duplicates appear
- What non-residual lines look like (warnings, headers, status messages)

## Complete monitoring script skeleton

Combines all patterns: auth, conditional reset, `stream_task_all` for one-loop monitoring of logs + process tree + host resources.

```python
import time, ssl
from ansys.hps.client.auth.api.oidc_login import refresh_tokens, browser_login, save_tokens
from ansys.hps.client import Client
from ansys.hps.client.jms import ProjectApi
from ansys.hps.client.monitor import MonitorClient

HPS_URL = "https://myserver:8443/hps"

def monitor_job(project_id, job_id):
    # Auth — refresh first, browser login as fallback
    tokens = refresh_tokens(hps_url=HPS_URL, storage="keyring", verify_ssl=False)
    if not tokens:
        tokens = browser_login(HPS_URL, verify_ssl=False)
        save_tokens(tokens, HPS_URL, storage="keyring")
    client = Client(
        url=HPS_URL,
        access_token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token"),  # CRITICAL: enables auto-refresh for long runs
        verify=False,
    )
    project_api = ProjectApi(client, project_id)

    # Snapshot task IDs before reset so we can detect a recycled task ID
    old_ids = {t.id for t in project_api.get_tasks(job_id=job_id)}

    # Conditional reset — never reset a running job
    jobs = project_api.get_jobs(id=job_id)
    job = jobs[0]
    was_reset = False
    if job.eval_status in ("evaluated", "failed", "aborted"):
        job.eval_status = "pending"
        project_api.update_jobs([job])
        was_reset = True

    # Find running task — prefer a fresh task ID if HPS created one
    task_id = None
    deadline = time.time() + 600
    while time.time() < deadline:
        tasks = project_api.get_tasks(job_id=job_id)
        running = [t for t in tasks if t.eval_status == "running"]
        if running:
            fresh = [t for t in running if t.id not in old_ids]
            task_id = (fresh or running)[0].id
            break
        time.sleep(2)

    ws_opts = {"sslopt": {"cert_reqs": ssl.CERT_NONE}}

    # One MonitorClient — stream_task_all opens three WebSocket streams internally
    # and multiplexes them into a single generator. No manual threading needed.
    monitor = MonitorClient(client=client, ws_connection_options=ws_opts, timeout_seconds=300.0)

    for event in monitor.stream_task_all(
        task_id=task_id,
        job_id=job_id,          # auto-terminates when job reaches a terminal status
        project_id=project_id,  # optional — auto-resolved from task logs if omitted
        tail_only=was_reset,    # skip old-run history when task ID is recycled after reset
        backlog=2000,
    ):
        kind = event["kind"]   # "log" | "process_tree" | "host_resources"
        msg  = event["msg"]    # MonitorMessage

        if kind == "log":
            file = msg.get("file_path", "")           # all files tailed; dispatch by name
            process_log_message(msg, file)             # solver-specific — see solver skill

        elif kind == "process_tree":
            processes = _extract_processes(msg)        # see Process tree monitoring section
            handle_proc_snapshot(processes)

        elif kind == "host_resources":
            cpu, mem = _extract_host_metrics(msg)      # see Host CPU/memory monitoring section
            handle_host_snapshot(cpu, mem)

    # loop exits when job_id poller detects terminal status (within ~5 s of job finishing)
```

**When to use individual streams instead of `stream_task_all`:** if you only need one or two stream types, need a server-side `file_path` filter on logs (reduces WebSocket traffic), or need different `timeout_seconds` per stream. Call `stream_task_logs`, `stream_task_process_tree`, or `stream_task_host_resources` directly in those cases — all three accept `job_id`, `tail_only`, and `since`.
