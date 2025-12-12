# RealtimeX Python SDK

Python client library for RealtimeX real-time messaging service.

## Requirements

- Python 3.7+
- `python-socketio[client]` >= 5.10.0
- `requests` (for private channel auth)

## Installation

**pip**

```bash
pip install realtimex-python
```

## Quick Start

```python
from realtimex import RealtimeX

# Initialize
realtimex = RealtimeX('YOUR_API_KEY', {
    'cluster': 'eu',  # optional, default 'eu'
    'ws_host': 'ws.realtimex.net',  # optional
    'ws_port': 443,  # optional
    'encrypted': True,  # optional, default True
})

# Bind connection events
realtimex.connection.bind('connected', lambda: print('Connected!'))

# Connect to server
realtimex.connect()

# Subscribe to a channel
channel = realtimex.subscribe('my-channel')

# Listen for events
channel.bind('my-event', lambda data: print('Received:', data))

# Send client events
channel.trigger('client-my-event', {
    'message': 'Hello'
})
```

## API

### RealtimeX(api_key, options={})

Create a new RealtimeX instance.

**Options:**
- `cluster` (str): Cluster name, default `'eu'`
- `ws_host` (str): WebSocket host, default `'ws.realtimex.net'`
- `ws_port` (int): WebSocket port, default `443`
- `encrypted` (bool): Use WSS, default `True`

### Methods

#### subscribe(channel_name)

Subscribe to a channel.

```python
channel = realtimex.subscribe('my-channel')
```

#### unsubscribe(channel_name)

Unsubscribe from a channel.

```python
realtimex.unsubscribe('my-channel')
```

#### disconnect()

Disconnect from RealtimeX.

```python
realtimex.disconnect()
```

### Channel

#### bind(event, callback)

Bind to an event.

```python
channel.bind('my-event', lambda data: print(data))
```

#### unbind(event, callback=None)

Unbind from an event.

```python
channel.unbind('my-event')
```

#### trigger(event, data)

Trigger a client event (must be prefixed with `client-`).

⚠️ **Note:** Client events only work on `private-*` and `presence-*` channels. Public channels will drop client events.

```python
channel.trigger('client-my-event', {'message': 'Hello'})
```

#### bind_global(callback)

Bind to all events on the channel.

```python
channel.bind_global(lambda event, data: print(event, data))
```

## Events

**Event Flow:**

```
WebSocket Server → SDK Connection → SDK processes → Emits to user code

Example:
Server sends: realtimex_internal:subscription_succeeded
  ↓
SDK Connection receives and converts to: subscription_succeeded
  ↓
User binds: realtimex.connection.bind('subscription_succeeded', callback)
```

### 1. Connection Events

Events emitted by the connection object:

| Event | Description |
|-------|-------------|
| `connecting` | Client is attempting to connect |
| `connected` | Successfully connected, socket_id received |
| `disconnected` | Connection closed |

**Example:**

```python
realtimex.connection.bind('connected', lambda: print('Connected!'))
realtimex.connection.bind('disconnected', lambda: print('Disconnected'))
```

### 2. Channel Internal Events

Internal RealtimeX events sent by the server (bind on connection object):

| Event | Description |
|-------|-------------|
| `subscription_succeeded` | Channel subscription successful |
| `subscription_error` | Channel subscription failed |

**Example:**

```python
realtimex.connection.bind('subscription_succeeded', lambda data: print('Subscribed:', data))
realtimex.connection.bind('subscription_error', lambda err: print('Error:', err))
```

**Raw Internal Events from Server:**

You can also listen to raw internal events sent by the RealtimeX server:

| Event | Description |
|-------|-------------|
| `realtimex_internal:subscription_succeeded` | Channel subscription successful |
| `realtimex_internal:subscription_error` | Subscription error |
| `realtimex_internal:member_added` | New member joined presence channel |
| `realtimex_internal:member_removed` | Member left presence channel |

**Example:**

```python
# Listen to raw internal events (advanced usage)
channel.bind('realtimex_internal:subscription_succeeded',
             lambda data: print('Raw subscription event:', data))
channel.bind('realtimex_internal:member_added',
             lambda member: print('Raw member added:', member))
```

### 3. Channel Events

Custom user events sent on channels:

| Event | Description |
|-------|-------------|
| Any string | Events sent by server or other clients |
| `client-*` | Client events (must be prefixed with `client-`) |

⚠️ **Note:** Client events (`client-*`) only work on `private-*` and `presence-*` channels.

**Example:**

```python
channel.bind('new-message', lambda data: print(data))
channel.bind('user-joined', lambda user: print('User joined:', user))

# Send client event (only works on private/presence channels)
channel.trigger('client-typing', {'user': 'John'})
```

### 4. Presence Channel Events

Special events for presence channels:

| Event | Description |
|-------|-------------|
| `presence:subscription_succeeded` | You joined presence channel |
| `presence:member_added` | New user added |
| `presence:member_removed` | User left |

**Example:**

```python
presence = realtimex.subscribe('presence-chat')

presence.bind('presence:subscription_succeeded',
              lambda members: print('Members:', members))
presence.bind('presence:member_added',
              lambda member: print('Joined:', member))
presence.bind('presence:member_removed',
              lambda member: print('Left:', member))
```

## Public Channels

Public channels work immediately without any backend setup. Just subscribe and start listening!

```python
from realtimex import RealtimeX

realtimex = RealtimeX('YOUR_API_KEY')
realtimex.connect()

# Subscribe to public channel
channel = realtimex.subscribe('my-channel')

# Listen for events
channel.bind('my-event', lambda data: print('Received:', data))
```

⚠️ **Note:** Public channels do NOT support client events (`client-*`). Use private or presence channels for client-to-client messaging.

**No backend required!** ✅

---

## Private & Presence Channels

⚠️ **Requires YOUR backend** to generate auth tokens.

Private and presence channels require authentication. The SDK requests auth tokens from **YOUR backend**, not the RealtimeX server.

### ⚠️ Important: Where is the auth endpoint?

**The auth endpoint MUST be on YOUR backend, NOT on the RealtimeX server.**

- ✅ **Correct**: `auth_endpoint: 'http://localhost:8000/auth'` (your Flask/Django/Express server)
- ❌ **Wrong**: `auth_endpoint: 'http://localhost:3001/auth'` (RealtimeX WebSocket server)

**The SDK NEVER requests auth from the RealtimeX WebSocket server.** It only connects to it after getting the auth token from YOUR backend.

```
┌─────────────┐      HTTP POST       ┌──────────────┐
│  Python SDK │ ──────────────────> │ YOUR Backend │
│             │  (get auth token)    │  /auth       │
└─────────────┘                      └──────────────┘
       │                                     │
       │                                     ▼
       │                              Generate HMAC
       │                              auth token
       │                                     │
       │         auth token                  │
       │ <───────────────────────────────────┘
       │
       │         WebSocket + auth
       └──────────────────────────────────────────>
                                            ┌──────────────────┐
                                            │ RealtimeX Server │
                                            │  (validates)     │
                                            └──────────────────┘
```

### Authentication Behavior:

- **By default**: `auth_endpoint` and `auth_callback` are `None` → private channels will throw `ValueError`
- **Priority**: `auth_callback` overrides `auth_endpoint` if both are provided
- **Error**: If neither is set, SDK raises error when subscribing to `private-*` or `presence-*` channels

```python
# ❌ This will raise ValueError
realtimex = RealtimeX('API_KEY')
channel = realtimex.subscribe('private-test')  # ValueError: auth_callback or auth_endpoint required

# ✅ This works
realtimex = RealtimeX('API_KEY', {'auth_endpoint': 'http://localhost:8000/auth'})
channel = realtimex.subscribe('private-test')  # OK
```

### Option 1: With auth_endpoint (automatic):

```python
realtimex = RealtimeX('YOUR_API_KEY', {
    'ws_host': 'localhost',
    'ws_port': 3001,
    'encrypted': False,
    'auth_endpoint': 'http://localhost:8000/auth'  # YOUR backend auth endpoint
})

realtimex.connect()
channel = realtimex.subscribe('private-my-channel')  # SDK requests auth from YOUR backend
```

**Your backend `/auth` endpoint should:**

#### For Private Channels:

```python
# Example Flask endpoint for private channels
@app.route('/auth', methods=['POST'])
def auth_channel():
    data = request.json
    socket_id = data['socket_id']
    channel_name = data['channel_name']
    
    # Generate HMAC signature
    import hmac
    import hashlib
    
    string_to_sign = f"{socket_id}:{channel_name}"
    auth = hmac.new(
        YOUR_APP_SECRET.encode(),
        string_to_sign.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return {
        'auth': f"{YOUR_APP_KEY}:{auth}"
    }
```

#### For Presence Channels:

```python
# Example Flask endpoint for presence channels
import json

@app.route('/auth', methods=['POST'])
def auth_channel():
    data = request.json
    socket_id = data['socket_id']
    channel_name = data['channel_name']
    
    # Get user_data from request (sent by SDK)
    user_data = data.get('user_data', {})
    
    # Serialize user_data to JSON string
    channel_data = json.dumps(user_data)
    
    # Generate HMAC signature with channel_data
    import hmac
    import hashlib
    
    string_to_sign = f"{socket_id}:{channel_name}:{channel_data}"
    auth = hmac.new(
        YOUR_APP_SECRET.encode(),
        string_to_sign.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return {
        'auth': f"{YOUR_APP_KEY}:{auth}",
        'channel_data': channel_data
    }
```

### Option 2: With custom auth_callback:

```python
import requests

def authorizer(channel_name, socket_id):
    # Custom auth logic
    response = requests.post('http://localhost:3001/auth/channels', json={
        'channel_name': channel_name,
        'socket_id': socket_id
    })
    return response.json()  # Returns: {'auth': 'real_token', 'channel_data': '...'}

realtimex = RealtimeX('YOUR_API_KEY', 
    options={'ws_host': 'localhost', 'ws_port': 3001, 'encrypted': False},
    auth_callback=authorizer
)

realtimex.connect()
channel = realtimex.subscribe('private-my-channel')
```

### Presence channels with user data:

```python
realtimex = RealtimeX('YOUR_API_KEY',
    options={
        'ws_host': 'localhost',
        'ws_port': 3001,
        'encrypted': False,
        'auth_endpoint': 'http://localhost:8000/auth'  # YOUR backend
    },
    user_data={'user_id': '123', 'name': 'John'}
)

realtimex.connect()
channel = realtimex.subscribe('presence-room-1')
```

**Flow:**
```
Python SDK → YOUR Backend /auth → SDK gets auth token → RealtimeX WebSocket → Success
```

---

## Complete Working Example

Minimal working project with private channel authentication:

### 1. Install dependencies:

```bash
pip install realtimex-python flask
```

### 2. Create `server.py` (your auth backend):

```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import json

app = Flask(__name__)

APP_KEY = 'your_app_key'
APP_SECRET = 'your_app_secret'

@app.route('/auth', methods=['POST'])
def auth():
    data = request.json
    socket_id = data['socket_id']
    channel_name = data['channel_name']
    
    # Check if it's a presence channel
    if channel_name.startswith('presence-'):
        user_data = data.get('user_data', {})
        channel_data = json.dumps(user_data)
        
        string_to_sign = f"{socket_id}:{channel_name}:{channel_data}"
        auth_signature = hmac.new(
            APP_SECRET.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return jsonify({
            'auth': f"{APP_KEY}:{auth_signature}",
            'channel_data': channel_data
        })
    else:
        # Private channel
        string_to_sign = f"{socket_id}:{channel_name}"
        auth_signature = hmac.new(
            APP_SECRET.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return jsonify({
            'auth': f"{APP_KEY}:{auth_signature}"
        })

if __name__ == '__main__':
    app.run(port=8000)
```

### 3. Create `client.py`:

```python
from realtimex import RealtimeX
import time

API_KEY = 'your_api_key'

client = RealtimeX(API_KEY, {
    'ws_host': 'localhost',
    'ws_port': 3001,
    'encrypted': False,
    'auth_endpoint': 'http://localhost:8000/auth'
})

client.connection.bind('connected', lambda: print('✅ Connected!'))
client.connection.bind('subscription_succeeded', lambda data: print('✅ Subscribed:', data))

client.connect()

# Wait for connection
time.sleep(1)

# Subscribe to private channel
channel = client.subscribe('private-test-channel')
channel.bind('my-event', lambda data: print('📨 Received:', data))

# Keep alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    client.disconnect()
    print('👋 Disconnected')
```

### 4. Run:

```bash
# Terminal 1: Start auth server
python3 server.py

# Terminal 2: Start client
python3 client.py
```

**Expected output:**
```
✅ Connected!
✅ Subscribed: {'channel': 'private-test-channel', 'socket_id': '...'}
```

## License

MIT
