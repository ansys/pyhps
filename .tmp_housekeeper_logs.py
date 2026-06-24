import ssl as _ssl
import json
from ansys.hps.client import Client
import websocket

_ssl._create_default_https_context = _ssl._create_unverified_context

base = 'https://localhost:8443/hps'
client = Client(base, 'repadmin', 'repadmin', verify=False)

token = client.access_token
ws_url = 'wss://localhost:8443/hps/monitor/ws/topics'

print('=== Housekeeper service log stream ===', flush=True)
print(f'WS: {ws_url}', flush=True)
print('Press Ctrl+C to stop', flush=True)
print('-' * 80, flush=True)

ws = websocket.create_connection(
    ws_url,
    timeout=60,
    sslopt={"cert_reqs": _ssl.CERT_NONE},
    header={"Authorization": f"Bearer {token}"},
)

ws.send(json.dumps({
    'type': 'command',
    'action': 'subscribe',
    'topics': [{'client_type': 'ansys.rep.housekeeper'}],
    'backlog': {'limit': 200},
}))

count = 0
try:
    while True:
        raw = ws.recv()
        if not raw:
            print('[connection closed]', flush=True)
            break

        payload = json.loads(raw)
        messages = payload.get('messages', [payload]) if isinstance(payload, dict) else payload
        if not isinstance(messages, list):
            messages = [messages]

        for msg in messages:
            if not isinstance(msg, dict):
                continue
            ts = (msg.get('time') or msg.get('timestamp') or '')[:26]
            tags = msg.get('tags', {})
            level = tags.get('level', '?')
            host = tags.get('host', '?')
            text = msg.get('message', '')
            print(f'{ts} [{level}] [{host}] {text}', flush=True)
            count += 1
            if count >= 1000:
                print('[max 1000 messages reached]', flush=True)
                raise KeyboardInterrupt
except KeyboardInterrupt:
    print('\n[stream stopped]', flush=True)
except Exception as e:
    print(f'[stream ended: {e}]', flush=True)
finally:
    ws.close()
    print('-' * 80, flush=True)
    print(f'Total messages: {count}', flush=True)
