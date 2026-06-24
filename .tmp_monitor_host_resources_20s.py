import ssl as _ssl
import json
import time
import statistics
from datetime import datetime, UTC

from ansys.hps.client import Client
from ansys.hps.client.jms import JmsApi, ProjectApi
from ansys.hps.client.rms import RmsApi
import websocket

_ssl._create_default_https_context = _ssl._create_unverified_context

BASE = 'https://localhost:8443/hps'
USER = 'repadmin'
PWD = 'repadmin'
REPORT_SECONDS = 20

client = Client(BASE, USER, PWD, verify=False)

# Find running task
running = None
for p in JmsApi(client).get_projects():
    try:
        for t in ProjectApi(client, p.id).get_tasks():
            if str(getattr(t, 'eval_status', '')).lower() == 'running':
                running = (p.id, p.name, t.id, getattr(t, 'host_id', None))
                break
        if running:
            break
    except Exception:
        continue

if not running:
    print('No running task found.', flush=True)
    raise SystemExit(0)

project_id, project_name, task_id, host_id = running

# Resolve evaluator name
rms = RmsApi(client)
evaluator_name = None
for ev in rms.get_evaluators() or []:
    if getattr(ev, 'host_id', None) == host_id:
        evaluator_name = getattr(ev, 'name', None)
        break

if not evaluator_name:
    print(f'Could not resolve evaluator for host_id={host_id}', flush=True)
    raise SystemExit(1)

ws = websocket.create_connection(
    'wss://localhost:8443/hps/monitor/ws/topics',
    timeout=5,
    sslopt={'cert_reqs': _ssl.CERT_NONE},
    header={'Authorization': f'Bearer {client.access_token}'},
)

# Correct subscription path: evaluator_name + host_resources
ws.send(json.dumps({
    'type': 'command',
    'action': 'subscribe',
    'topics': [{
        'evaluator_name': evaluator_name,
        'client_type': 'ansys.rep.evaluator',
        'type': 'metric',
        'statistic': 'host_resources',
    }],
    'backlog': {'limit': 20},
}))

print(f'Monitoring task: {task_id} | project: {project_name} ({project_id})', flush=True)
print(f'Using evaluator_name host_resources: {evaluator_name} (host_id={host_id})', flush=True)
print('Reporting every 20 seconds', flush=True)
print('-' * 118, flush=True)
print('window_end_utc           samples   cpu_latest   cpu_min   cpu_max   cpu_avg   mem_latest   mem_min   mem_max   mem_avg', flush=True)

cpu_vals = []
mem_vals = []
latest_cpu = None
latest_mem = None
window_start = time.time()

while True:
    now = time.time()
    if now - window_start >= REPORT_SECONDS:
        ts = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
        if cpu_vals or mem_vals:
            def _stats(vals, latest):
                if not vals:
                    return ('n/a', 'n/a', 'n/a', 'n/a')
                return (
                    f'{latest:.3f}' if latest is not None else 'n/a',
                    f'{min(vals):.3f}',
                    f'{max(vals):.3f}',
                    f'{statistics.mean(vals):.3f}',
                )
            c_latest, c_min, c_max, c_avg = _stats(cpu_vals, latest_cpu)
            m_latest, m_min, m_max, m_avg = _stats(mem_vals, latest_mem)
            print(f'{ts}   {max(len(cpu_vals), len(mem_vals)):>7}   {c_latest:>10}   {c_min:>7}   {c_max:>7}   {c_avg:>7}   {m_latest:>10}   {m_min:>7}   {m_max:>7}   {m_avg:>7}', flush=True)
        else:
            print(f'{ts}   {0:>7}   no metric samples', flush=True)

        # Stop if task is no longer running
        try:
            status = None
            for t in ProjectApi(client, project_id).get_tasks():
                if t.id == task_id:
                    status = str(getattr(t, 'eval_status', '')).lower()
                    break
            if status and status != 'running':
                print(f'Task status changed to {status}. Stopping monitor.', flush=True)
                break
        except Exception:
            pass

        window_start = now
        cpu_vals = []
        mem_vals = []

    try:
        raw = ws.recv()
    except websocket._exceptions.WebSocketTimeoutException:
        continue

    if not raw:
        continue

    payload = json.loads(raw)
    messages = payload.get('messages', [payload]) if isinstance(payload, dict) else payload
    if not isinstance(messages, list):
        messages = [messages]

    for msg in messages:
        if not isinstance(msg, dict):
            continue
        text = msg.get('message')
        if not text:
            continue
        try:
            metric = json.loads(text)
        except Exception:
            continue

        cpu_usage = None
        mem_pct = None

        cpu_obj = metric.get('cpu') if isinstance(metric, dict) else None
        vm_obj = metric.get('virtual_memory') if isinstance(metric, dict) else None

        if isinstance(cpu_obj, dict):
            cpu_usage = cpu_obj.get('usage')

        if isinstance(vm_obj, dict):
            if vm_obj.get('percent') is not None:
                mem_pct = vm_obj.get('percent')
            else:
                total = vm_obj.get('total')
                avail = vm_obj.get('available')
                if isinstance(total, (int, float)) and total:
                    if isinstance(avail, (int, float)):
                        mem_pct = (1.0 - (avail / total)) * 100.0

        try:
            if cpu_usage is not None:
                latest_cpu = float(cpu_usage)
                cpu_vals.append(latest_cpu)
            if mem_pct is not None:
                latest_mem = float(mem_pct)
                mem_vals.append(latest_mem)
        except Exception:
            continue

ws.close()
