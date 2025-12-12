from typing import Dict, Optional, Callable
import json
from .connection import Connection
from .channel import Channel
from .types import RealtimeXOptions


class RealtimeX:
    def __init__(self, api_key: str, options: Optional[RealtimeXOptions] = None, 
                 auth_callback: Optional[Callable[[str, str], str]] = None,
                 user_data: Optional[Dict] = None):
        self.api_key = api_key
        self.options = self._merge_options(options or {})
        self.auth_callback = auth_callback
        self.user_data = user_data or {}
        self.channels: Dict[str, Channel] = {}
        
        url = self._build_url()
        self.connection = Connection(url)
        self._setup_connection_handlers()
        # Don't auto-connect - let user bind events first, then call connect()

    def connect(self) -> None:
        """Connect to RealtimeX server."""
        self.connection.connect()

    def _setup_connection_handlers(self) -> None:
        # Route server-event messages to channels
        self.connection.bind('message', self._route_to_channel)

    def subscribe(self, channel_name: str) -> Channel:
        if channel_name in self.channels:
            return self.channels[channel_name]

        channel = Channel(channel_name, self)
        self.channels[channel_name] = channel

        subscribe_data = self._build_subscribe_data(channel_name)
        self.connection.send({'event': 'subscribe', 'data': subscribe_data})
        
        return channel

    def _build_subscribe_data(self, channel_name: str) -> Dict:
        """Build subscribe data with auth for private/presence channels."""
        data = {'channel': channel_name}
        
        if self._is_private_channel(channel_name):
            if not self.auth_callback:
                raise ValueError(f"Cannot subscribe to {channel_name}: auth_callback is required for private/presence channels")
            
            auth_data = self._get_auth_data(channel_name)
            data.update(auth_data)
        
        return data

    def _is_private_channel(self, channel_name: str) -> bool:
        """Check if channel requires authentication."""
        return channel_name.startswith('private-') or channel_name.startswith('presence-')

    def _get_auth_data(self, channel_name: str) -> Dict:
        """Get auth data from callback."""
        socket_id = self.connection.socket_id or ''
        auth_result = self.auth_callback(channel_name, socket_id)
        
        auth_data = {}
        if isinstance(auth_result, dict):
            auth_data['auth'] = auth_result.get('auth')
            if 'channel_data' in auth_result:
                auth_data['channel_data'] = auth_result.get('channel_data')
        else:
            auth_data['auth'] = auth_result
        
        # For presence channels add user_data if not provided
        if channel_name.startswith('presence-') and 'channel_data' not in auth_data:
            auth_data['channel_data'] = json.dumps(self.user_data)
        
        return auth_data

    def unsubscribe(self, channel_name: str) -> None:
        if channel_name not in self.channels:
            return

        # Send unsubscribe event like JS SDK
        self.connection.send({
            'event': 'unsubscribe',
            'data': {'channel': channel_name}
        })
        del self.channels[channel_name]

    def disconnect(self) -> None:
        self.connection.disconnect()
        self.channels.clear()

    def _merge_options(self, options: RealtimeXOptions) -> RealtimeXOptions:
        defaults = {
            'cluster': 'eu',
            'ws_host': 'ws.realtimex.net',
            'ws_port': 443,
            'encrypted': True
        }
        return {**defaults, **options}

    def _build_url(self) -> str:
        protocol = 'https' if self.options['encrypted'] else 'http'
        host = self.options['ws_host']
        port = self.options['ws_port']
        
        return f"{protocol}://{host}:{port}?api_key={self.api_key}"

    def _route_to_channel(self, message: Dict) -> None:
        # Route server-event to appropriate channel
        channel_name = message.get('channel')
        event_name = message.get('event')
        event_data = message.get('data')
        
        if channel_name and channel_name in self.channels:
            self.channels[channel_name]._handle_event(event_name, event_data)
