import ssl as _ssl
import json
import datetime
from ansys.hps.client import Client
import websocket

_ssl._create_default_https_context = _ssl._create_unverified_context

hps_client = Client('https://localhost:8443/hps', 'repadmin', 'repadmin', verify=False)
task_id = '033VtLzk09E7xRBeebJDJm'
token = hps_client.access_token

# Correct WS path: /hps/monitor/ws (Traefik strips /hps/monitor/ws, adds /dcs/monitor/ws, routes to port 1092)
ws_url = 'wss://localhost:8443/hps/monitor/ws/topics'

print(f'Streaming task log files for task {task_id}...', flush=True)
print(f'WS URL: {ws_url}', flush=True)
print('Press Ctrl+C to stop.', flush=True)
print('-' * 60, flush=True)

ws = websocket.create_connection(
    ws_url,
    timeout=30,
    sslopt={"cert_reqs": _ssl.CERT_NONE},
    header={"Authorization": f"Bearer {token}"},
)

command = {
    "type": "command",
    "action": "subscribe",
    "topics": [{"task_id": task_id, "client_type": "ansys.rep.evaluator.file_tail"}],
    "backlog": {"limit": 200},
}
ws.send(json.dumps(command))

msg_count = 0
try:
    while True:
        raw = ws.recv()
        if not raw:
            print('[connection closed]', flush=True)
            break
        msg = json.loads(raw)
        ts = msg.get('timestamp', '')[:19]
        file_path = msg.get('tags', {}).get('file_path', '')
        text = msg.get('message', msg.get('text', repr(msg)))
        label = f'[{file_path}]' if file_path else ''
        print(f'{ts} {label} {text}', flush=True)
        msg_count += 1
        if msg_count >= 1000:
            print('[max messages reached]', flush=True)
            break
except KeyboardInterrupt:
    print('\n[interrupted]', flush=True)
finally:
    ws.close()
    print(f'Total messages: {msg_count}', flush=True)
