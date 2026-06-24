import ssl as _ssl
import json
import time
import statistics
from datetime import datetime

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
jms = JmsApi(client)
running = None
for p in jms.get_projects():
    try:
        tasks = list(ProjectApi(client, p.id).get_tasks())
    except Exception:
        continue
    for t in tasks:
        if str(getattr(t, 'eval_status', '')).lower() == 'running':
            running = (p.id, p.name, t.id, getattr(t, 'host_id', None))
            break
    if running:
        break

if not running:
    print('No running task found.', flush=True)
    raise SystemExit(0)

project_id, project_name, task_id, host_id = running
if not host_id:
    print(f'Running task {task_id} has no host_id; cannot resolve evaluator.', flush=True)
    raise SystemExit(1)

# Resolve evaluator name through RMS
evaluator_name = None
rms = RmsApi(client)
for ev in rms.get_evaluators() or []:
    if getattr(ev, 'host_id', None) == host_id:
        evaluator_name = getattr(ev, 'name', None)
        break

if not evaluator_name:
    print(f'Could not resolve evaluator name for host_id={host_id}', flush=True)
    raise SystemExit(1)

ws_url = 'wss://localhost:8443/hps/monitor/ws/topics'
ws = websocket.create_connection(
    ws_url,
    timeout=5,
    sslopt={'cert_reqs': _ssl.CERT_NONE},
    header={'Authorization': f'Bearer {client.access_token}'},
)

ws.send(json.dumps({
    'type': 'command',
    'action': 'subscribe',
    'topics': [{
        'evaluator_name': evaluator_name,
        'client_type': 'ansys.rep.evaluator',
        'type': 'metric',
        'statistic': 'process_tree',
    }],
    'backlog': {'limit': 30},
}))

print(f'Monitoring running task: {task_id} | project: {project_name} ({project_id})', flush=True)
print(f'Host: {host_id} | evaluator: {evaluator_name}', flush=True)
print('Reporting every 20 seconds (CPU% and MEM% from process_tree)', flush=True)
print('-' * 120, flush=True)
print('window_end_utc           samples   cpu_latest   cpu_min   cpu_max   cpu_avg   mem_latest   mem_min   mem_max   mem_avg', flush=True)

cpu_vals = []
mem_vals = []
latest_cpu = None
latest_mem = None
window_start = time.time()

while True:
    now = time.time()
    if now - window_start >= REPORT_SECONDS:
        ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        if cpu_vals or mem_vals:
            def _fmt(vals, latest):
                if not vals:
                    return ('n/a', 'n/a', 'n/a', 'n/a')
                return (
                    f'{latest:.3f}' if latest is not None else 'n/a',
                    f'{min(vals):.3f}',
                    f'{max(vals):.3f}',
                    f'{statistics.mean(vals):.3f}',
                )
            c_latest, c_min, c_max, c_avg = _fmt(cpu_vals, latest_cpu)
            m_latest, m_min, m_max, m_avg = _fmt(mem_vals, latest_mem)
            print(f'{ts}   {max(len(cpu_vals), len(mem_vals)):>7}   {c_latest:>10}   {c_min:>7}   {c_max:>7}   {c_avg:>7}   {m_latest:>10}   {m_min:>7}   {m_max:>7}   {m_avg:>7}', flush=True)
        else:
            print(f'{ts}   {0:>7}   no metric samples', flush=True)

        # Stop if task finished
        status = None
        try:
            for t in ProjectApi(client, project_id).get_tasks():
                if t.id == task_id:
                    status = str(getattr(t, 'eval_status', '')).lower()
                    break
        except Exception:
            status = None
        if status and status != 'running':
            print(f'Task status changed to {status}. Stopping monitor.', flush=True)
            break

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
            proc = json.loads(text)
        except Exception:
            continue
        cpu = proc.get('cpu_percentage')
        mem = proc.get('memory_percentage')
        try:
            if cpu is not None:
                latest_cpu = float(cpu)
                cpu_vals.append(latest_cpu)
            if mem is not None:
                latest_mem = float(mem)
                mem_vals.append(latest_mem)
        except Exception:
            continue

ws.close()
