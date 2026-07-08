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

**Critical**: use `backlog=0` after a fresh job reset. If the task ID is reused across runs (HPS increments `trial_number` on the same task), the old run's messages are still in the backlog. With `backlog=2000` they replay immediately, filling `seen_iters` with ITER:1-100, which then silently blocks all live iterations from the new run.

```python
# was_reset = True when job.eval_status was evaluated/failed/aborted before reset
backlog = 0 if was_reset else 2000
for msg in monitor.stream_task_logs(task_id=task_id, backlog=backlog):
    ...
```

## Done detection — use a background polling thread

`stream_task_logs` does not automatically stop when the task finishes. Any check inside the `for msg in ...` loop only runs when a message arrives. After the final iteration the solver finishes post-processing (can take minutes), then HPS marks the task done — but no more WebSocket messages arrive. The loop blocks for `timeout_seconds` before it can check.

**Use a daemon thread that polls every 5 s independently of the stream:**

```python
import threading
done_event = threading.Event()

def poll_done():
    while not done_event.is_set():
        done_event.wait(timeout=5)
        if done_event.is_set():
            return
        try:
            tasks = project_api.get_tasks(job_id=JOB_ID)
            cur = next((t for t in tasks if t.id == task_id), None)
            if cur and cur.eval_status in ("evaluated", "failed", "aborted"):
                print(f"DONE:{cur.eval_status}", flush=True)
                done_event.set()
        except Exception:
            pass  # transient error — keep polling

threading.Thread(target=poll_done, daemon=True).start()

try:
    for msg in monitor.stream_task_logs(task_id=task_id, backlog=backlog):
        if done_event.is_set():
            return
        # ... parse msg, update plot ...
finally:
    done_event.set()  # always stop the poller when stream exits
```

This guarantees DONE is detected within 5 s of the task status changing, regardless of WebSocket message arrival.

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

```python
import json, threading, ssl
from ansys.hps.client.monitor import MonitorClient

def _extract_processes(msg):
    """Parse process tree from msg["message"] (a JSON string), flatten recursively."""
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
- `msg.get("processes", [])` always returns `[]` — that key does not exist.
- `cpu_percentage` and `memory_percentage` are **strings**, not floats — cast with `float()` before arithmetic.
- Root node has `children` list — must recurse to flatten; top-level processes are NOT a flat list.

## Host CPU/memory monitoring

`MonitorClient.stream_task_host_resources` streams host-level CPU and memory snapshots. Same message pattern as process tree — `msg["message"]` is a JSON string.

```python
def _extract_host_metrics(msg):
    """msg["message"] JSON: {"cpu": {"usage": X}, "virtual_memory": {"percent": Y}, ...}"""
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

**Key difference from process tree**: `stream_task_host_resources` requires `project_id` as a named argument. It uses JMS/RMS to resolve which evaluator host is running the task. The MonitorClient can also auto-resolve it via `monitor.resolve_project_id_for_task(task_id=task_id)` if you don't have it handy.

## Complete monitoring script skeleton

Combines all patterns: auth, conditional reset, backlog, background poller, optional process tree + host streams.

```python
import json, time, ssl, threading
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
    done_event = threading.Event()

    # Optional: process tree stream (separate MonitorClient — cannot share WebSocket)
    def stream_proc_tree():
        proc_mon = MonitorClient(client=client, ws_connection_options=ws_opts, timeout_seconds=60.0)
        try:
            for snap in proc_mon.stream_task_process_tree(task_id=task_id, backlog=1):
                if done_event.is_set():
                    return
                processes = _extract_processes(snap)   # see Process tree monitoring section
                handle_proc_snapshot(processes)
        except Exception as exc:
            print(f"PROC_ERROR:{exc}", flush=True)

    threading.Thread(target=stream_proc_tree, daemon=True).start()

    # Optional: host CPU/memory stream (requires project_id)
    def stream_host():
        host_mon = MonitorClient(client=client, ws_connection_options=ws_opts, timeout_seconds=60.0)
        try:
            for snap in host_mon.stream_task_host_resources(
                task_id=task_id, project_id=project_id, backlog=5
            ):
                if done_event.is_set():
                    return
                cpu, mem = _extract_host_metrics(snap)   # see Host CPU/memory monitoring section
                handle_host_snapshot(cpu, mem)
        except Exception as exc:
            print(f"HOST_ERROR:{exc}", flush=True)

    threading.Thread(target=stream_host, daemon=True).start()

    # Background poller — DONE detection independent of WebSocket message arrival
    def poll_done():
        while not done_event.is_set():
            done_event.wait(timeout=5)
            if done_event.is_set():
                return
            try:
                tasks = project_api.get_tasks(job_id=job_id)
                cur = next((t for t in tasks if t.id == task_id), None)
                if cur and cur.eval_status in ("evaluated", "failed", "aborted"):
                    print(f"DONE:{cur.eval_status}", flush=True)
                    done_event.set()
            except Exception:
                pass

    threading.Thread(target=poll_done, daemon=True).start()

    # Log stream — backlog=0 after reset to avoid replaying previous trial
    backlog = 0 if was_reset else 2000
    monitor = MonitorClient(client=client, ws_connection_options=ws_opts, timeout_seconds=300.0)
    try:
        for msg in monitor.stream_task_logs(task_id=task_id, backlog=backlog):
            if done_event.is_set():
                return
            process_log_message(msg)   # solver-specific — see solver skill
    finally:
        done_event.set()   # always stop background threads when stream exits
```
