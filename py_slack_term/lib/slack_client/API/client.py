from typing import Optional, Union

from .channel import Channel
from .user import User
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse


class SlackApiClient:
    PUBLIC = 'public_channel'
    PRIVATE = 'private_channel'
    IM = 'im'
    MPIM = 'mpim'

    def __init__(self, config):
        self.token: str = config.token
        self.socket_mode_token: Optional[str] = getattr(config, 'socket_mode_token', None)
        self.web_client: WebClient = WebClient(token=self.token)
        self.channels = {}
        self.users = {}
        self.rtm_url: Optional[str] = None
        self.socket_mode_client: Optional[SocketModeClient] = None
        self.on_socket_mode_response = None
        self.refresh_user_list()
        self.refresh_channel_list()

    def refresh_channel_list(self) -> None:
        channels = []
        channels.extend(self.get_my_channels(_type=self.PUBLIC))
        channels.extend(self.get_my_channels(_type=self.PRIVATE))
        channels.extend(self.get_my_channels(_type=self.IM))
        channels.extend(self.get_my_channels(_type=self.MPIM))
        unique = {str(c.id): c for c in channels}
        self.channels = dict(sorted(unique.items(), key=lambda item: item[1].name.lower()))

    def get_public_channels(self) -> list:
        response = self.web_client.conversations_list(types=self.PUBLIC, exclude_archived=True)
        if response.get('ok'):
            return [Channel(self, item, load_details=False) for item in response.get('channels', [])]
        return []

    def get_my_channels(self, _type: str = None) -> list:
        if _type is None:
            types = (self.PUBLIC, self.PRIVATE, self.IM, self.MPIM)
        else:
            types = [_type]

        channels = []
        for t in types:
            response = self.web_client.users_conversations(types=t)
            if response.get('ok'):
                channels.extend(Channel(self, item, load_details=False) for item in response.get('channels', []))
        return channels

    def refresh_user_list(self) -> None:
        self.users = {str(u.id): u for u in self.get_users()}

    def get_active_channels(self) -> list:
        response = self.web_client.conversations_list(exclude_archived=True)
        if response.get('ok'):
            return [Channel(self, item, load_details=False) for item in response.get('channels', [])]
        return []

    def get_active_channels_im_in(self) -> list:
        return list(self.channels.values())

    def get_users(self) -> list:
        response = self.web_client.users_list()
        if response.get('ok'):
            return [User(r) for r in response.get('members')]
        return []

    def find_user(self, query: str) -> Optional[User]:
        query = (query or '').strip().lower()
        if not query:
            return None

        candidates = list(self.users.values())
        exact_fields = ('id', 'name', 'display_name', 'real_name')
        for field in exact_fields:
            for user in candidates:
                value = getattr(user, field, None)
                if value and str(value).lower() == query:
                    return user

        for user in candidates:
            for field in exact_fields:
                value = getattr(user, field, None)
                if value and str(value).lower().startswith(query):
                    return user

        for user in candidates:
            for field in exact_fields:
                value = getattr(user, field, None)
                if value and query in str(value).lower():
                    return user
        return None

    def create_channel(self, name: str) -> Channel:
        name = name.strip().lstrip('#').lower().replace(' ', '-')
        response = self.web_client.conversations_create(name=name)
        if not response.get('ok'):
            raise SlackApiError("Failed to create channel", response=response)
        channel = Channel(self, response.get('channel'), load_details=False)
        self.channels[str(channel.id)] = channel
        return channel

    def open_dm(self, user_or_query: Union[User, str]) -> Channel:
        if isinstance(user_or_query, User):
            user = user_or_query
        else:
            user = self.find_user(user_or_query)
        if user is None:
            raise ValueError(f'No Slack user matched {user_or_query!r}')

        response = self.web_client.conversations_open(users=[user.id])
        if not response.get('ok'):
            raise SlackApiError("Failed to open DM", response=response)
        channel = Channel(self, response.get('channel'), load_details=False)
        self.channels[str(channel.id)] = channel
        return channel

    def rtm_connect(self) -> str:
        """Deprecated RTM connect — kept for backward compatibility."""
        response = self.web_client.rtm_connect()
        if response.get('ok'):
            return response.get('url')

    def socket_mode_connect(self, on_message_handler) -> None:
        """
        Connect using Socket Mode instead of deprecated RTM.

        Socket Mode is Slack's recommended real-time messaging transport.
        It uses WebSocket over WSS instead of requiring public IP + port.
        """
        if not self.socket_mode_token:
            raise ValueError(
                "Socket Mode token not configured. "
                "Add it to your config.yml or set SLACK_APP_TOKEN env var."
            )

        def on_request(client, request: SocketModeRequest) -> None:
            client.send_socket_mode_response(SocketModeResponse(envelope_id=request.envelope_id))
            payload = request.payload or {}
            if request.type == 'events_api':
                event = payload.get('event') or {}
                if event:
                    on_message_handler(event)
            elif request.type == 'interactive':
                on_message_handler(payload)

        self.socket_mode_client = SocketModeClient(
            app_token=self.socket_mode_token,
            web_client=self.web_client,
            on_message_listeners=[],
            on_error_listeners=[],
            on_close_listeners=[]
        )
        self.socket_mode_client.socket_mode_request_listeners.append(on_request)
        self.socket_mode_client.connect()

    def socket_mode_disconnect(self) -> None:
        """Disconnect the Socket Mode client."""
        if self.socket_mode_client:
            self.socket_mode_client.close()
            self.socket_mode_client = None
