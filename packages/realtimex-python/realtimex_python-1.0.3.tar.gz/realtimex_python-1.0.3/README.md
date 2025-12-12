# RealtimeX Python SDK

Python client library for RealtimeX real-time messaging service.

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

```python
channel.trigger('client-my-event', {'message': 'Hello'})
```

#### bind_global(callback)

Bind to all events on the channel.

```python
channel.bind_global(lambda event, data: print(event, data))
```

### Connection Events

```python
realtimex.connection.bind('connecting', lambda: print('Connecting...'))
realtimex.connection.bind('connected', lambda: print('Connected!'))
realtimex.connection.bind('disconnected', lambda: print('Disconnected'))
```

## Private Channels

### With auth callback:

```python
import requests

def authorizer(channel_name, socket_id):
    # Request auth from your server
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
    options={'ws_host': 'localhost', 'ws_port': 3001, 'encrypted': False},
    auth_callback=authorizer,
    user_data={'user_id': '123', 'name': 'John'}
)

realtimex.connect()
channel = realtimex.subscribe('presence-room-1')
```

**Note:** `auth_callback` is required for private/presence channels. It should return either:
- A dict: `{'auth': 'token', 'channel_data': '...'}`
- A string: `'auth_token'` (for simple cases)

## License

MIT
