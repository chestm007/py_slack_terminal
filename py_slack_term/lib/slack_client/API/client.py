import asyncio

from .channel import Channel
from .user import User
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient


class SlackApiClient:
    PUBLIC = 'public_channel'
    PRIVATE = 'private_channel'
    IM = 'im'
    MPIM = 'mpim'

    def __init__(self, config):
        self.token: str = config.token
        self.socket_mode_token: str = getattr(config, 'socket_mode_token', None)
        self.web_client: WebClient = WebClient(token=self.token)
        self.channels = {}
        self.users = {}
        self.rtm_url: str = None
        self.socket_mode_client: SocketModeClient = None
        self.on_socket_mode_response = None
        self.refresh_user_list()
        self.refresh_channel_list()

    def refresh_channel_list(self) -> None:
        channels = self.get_my_channels(_type=self.PUBLIC)
        channels.sort(key=lambda c: c.name)
        self.channels = {str(c.id): c for c in channels}

        private_channels = self.get_my_channels(_type=self.PRIVATE)
        private_channels.sort(key=lambda c: c.name)
        self.channels.update({str(c.id): c for c in private_channels})

        im_channels = self.get_my_channels(_type=self.IM)
        im_channels.sort(key=lambda c: c.name)
        self.channels.update({str(c.id): c for c in im_channels})

    def get_my_channels(self, _type: str=None) -> list:
        """Fetch all channels using manual cursor-based pagination."""
        if _type is None:
            types = (self.PUBLIC, self.PRIVATE, self.IM, self.MPIM)
        else:
            types = [_type]

        all_channels = []
        for t in types:
            cursor = None
            while True:
                kwargs = {'types': t}
                if cursor:
                    kwargs['cursor'] = cursor
                response = self.web_client.users_conversations(**kwargs)
                if response.get('ok'):
                    for item in response.get('channels'):
                        try:
                            ch = Channel(self, item)
                            if ch is not None:
                                all_channels.append(ch)
                        except Exception:
                            # Skip channels that fail to construct
                            pass
                    cursor = response.get('response_metadata', {}).get('next_cursor')
                    if not cursor:
                        break
                else:
                    break
        return all_channels

    def refresh_user_list(self) -> None:
        self.users = {str(u.id): u for u in self.get_users()}

    def get_active_channels(self) -> list:
        response = self.web_client.conversations_list(exclude_archived=True)
        if response.get('ok'):
            return [Channel(self, **item) for item in response.get('channels')]

    def get_active_channels_im_in(self) -> list:
        return list(self.channels.values())

    def get_users(self) -> list:
        response = self.web_client.users_list()
        if response.get('ok'):
            return [User(r) for r in response.get('members')]

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

        self.socket_mode_client = SocketModeClient(
            app_token=self.socket_mode_token,
            web_client=self.web_client,
            on_message_listeners=[on_message_handler]
        )
        self.socket_mode_client.connect()

    def socket_mode_disconnect(self) -> None:
        """Disconnect the Socket Mode client."""
        if self.socket_mode_client:
            self.socket_mode_client.close()
            self.socket_mode_client = None
