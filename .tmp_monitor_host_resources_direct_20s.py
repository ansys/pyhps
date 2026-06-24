import ssl as _ssl
import json
import time
import statistics
from datetime import datetime, UTC

from ansys.hps.client import Client
from ansys.hps.client.jms import JmsApi, ProjectApi
from ansys.hps.client.monitor.api.monitor_api import MonitorClient

_ssl._create_default_https_context = _ssl._create_unverified_context

BASE = 'https://localhost:8443/hps'
REPORT_SECONDS = 20

hps = Client(BASE, 'repadmin', 'repadmin', verify=False)

running = None
for p in JmsApi(hps).get_projects():
    try:
        for t in ProjectApi(hps, p.id).get_tasks():
            if str(getattr(t, 'eval_status', '')).lower() == 'running':
                running = (p.id, p.name, t.id)
                break
        if running:
            break
    except Exception:
        continue

if not running:
    print('No running task found.', flush=True)
    raise SystemExit(0)

project_id, project_name, task_id = running

mon = MonitorClient(
    base_url=BASE,
    token=hps.access_token,
    client=hps,
    ws_connection_options={'sslopt': {'cert_reqs': _ssl.CERT_NONE}},
    timeout_seconds=30,
)

print(f'Monitoring task: {task_id} | project: {project_name} ({project_id})', flush=True)
print('Source: MonitorClient.stream_task_host_resources (evaluator resolved internally)', flush=True)
print('Reporting every 20 seconds', flush=True)
print('-' * 118, flush=True)
print('window_end_utc           samples   cpu_latest   cpu_min   cpu_max   cpu_avg   mem_latest   mem_min   mem_max   mem_avg', flush=True)

cpu_vals = []
mem_vals = []
latest_cpu = None
latest_mem = None
window_start = time.time()

for msg in mon.stream_task_host_resources(task_id=task_id, backlog=20, max_messages=5000):
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

        try:
            status = None
            for t in ProjectApi(hps, project_id).get_tasks():
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

    text = msg.get('message') if isinstance(msg, dict) else None
    if not text:
        continue

    try:
        payload = json.loads(text)
    except Exception:
        continue

    cpu_usage = None
    mem_pct = None

    if isinstance(payload, dict):
        cpu_obj = payload.get('cpu')
        vm_obj = payload.get('virtual_memory')
        if isinstance(cpu_obj, dict):
            cpu_usage = cpu_obj.get('usage')
        if isinstance(vm_obj, dict):
            if vm_obj.get('percent') is not None:
                mem_pct = vm_obj.get('percent')
            else:
                total = vm_obj.get('total')
                avail = vm_obj.get('available')
                if isinstance(total, (int, float)) and total and isinstance(avail, (int, float)):
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

print('Monitor finished.', flush=True)
