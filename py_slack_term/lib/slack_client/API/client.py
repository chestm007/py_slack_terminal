import asyncio

from .channel import Channel
from .user import User
from slackclient import SlackClient


class SlackApiClient:
    PUBLIC = 'public_channel'
    PRIVATE = 'private_channel'
    IM = 'im'
    MPIM = 'mpim'

    def __init__(self, config):
        self.token: str = config.token
        self.slackclient: SlackClient = SlackClient(self.token)
        self.channels = {}
        self.users = {}
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
        async def channel_scraper_thread(t):
            response = self.slackclient.api_call('users.conversations',
                                                 types=t)
            if response.get('ok'):
                print('fetching channel info for type {}...'.format(t))
                loop = asyncio.get_event_loop()
                futures = []
                for item in response.get('channels'):
                    futures.append(loop.run_in_executor(None, Channel, self, item))
                responses = [await f for f in futures]
                return responses

        channels = {}
        if _type is None:
            types = (self.PUBLIC, self.PRIVATE, self.IM, self.MPIM)
        else:
            types = [_type]
        for t in types:
                loop = asyncio.get_event_loop()
                responses = loop.run_until_complete(channel_scraper_thread(t))
                channels[t] = [r for r in responses if r is not None]
        return channels.get(_type) if _type else channels

    def refresh_user_list(self) -> None:
        self.users = {str(u.id): u for u in self.get_users()}

    def get_active_channels(self) -> list:
        response = self.slackclient.api_call("channels.list", exclude_archived=1)
        if response.get('ok'):
            return [Channel(self, **item) for item in response.get('channels')]

    def get_active_channels_im_in(self) -> list:
        return list(self.channels.values())

    def get_users(self) -> list:
        response = self.slackclient.api_call('users.list')
        if response.get('ok'):
            return [User(r) for r in response.get('members')]

    def rtm_connect(self) -> str:
        response = self.slackclient.api_call('rtm.connect')
        if response.get('ok'):
            return response.get('url')
