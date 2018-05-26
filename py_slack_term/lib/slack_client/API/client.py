import pprint
import time

from ....lib import Config
from .channel import Channel
from .user import User
from slackclient import SlackClient

from py_slack_term.lib.slack_client.RTM import SlackRTMClient


class SlackApiClient:
    PUBLIC = 'public_channel'
    PRIVATE = 'private_channel'
    IM = 'im'
    MPIM = 'mpim'

    def __init__(self, config):
        self.token = config.token
        self.slackclient = SlackClient(self.token)
        self.channels = {}
        self.users = {}
        self.refresh_user_list()
        self.refresh_channel_list()

    def refresh_channel_list(self):
        channels = self.get_my_channels(_type=self.PUBLIC)
        channels.sort(key=lambda c: c.name)
        self.channels = {str(c.id): c for c in channels}

        private_channels = self.get_my_channels(_type=self.PRIVATE)
        private_channels.sort(key=lambda c: c.name)
        self.channels.update({str(c.id): c for c in private_channels})

        im_channels = self.get_my_channels(_type=self.IM)
        im_channels.sort(key=lambda c: c.name)
        self.channels.update({str(c.id): c for c in im_channels})

    def get_my_channels(self, _type=None):
        channels = {}
        if _type is None:
            types = (self.PUBLIC, self.PRIVATE, self.IM, self.MPIM)
        else:
            types = [_type]
        for t in types:
            response = self.slackclient.api_call('users.conversations',
                                                 types=t)
            if response.get('ok'):
                channels[t] = [Channel(self, **item) for item in response.get('channels')]
        return channels.get(_type) if _type else channels

    def refresh_user_list(self):
        self.users = {str(u.id): u for u in self.get_users()}

    def get_active_channels(self):
        response = self.slackclient.api_call("channels.list", exclude_archived=1)
        if response.get('ok'):
            return [Channel(self, **item) for item in response.get('channels')]

    def get_active_channels_im_in(self):
        return list(self.channels.values())

    def get_users(self):
        response = self.slackclient.api_call('users.list')
        if response.get('ok'):
            return [User(r) for r in response.get('members')]

    def rtm_connect(self) -> str:
        response = self.slackclient.api_call('rtm.connect')
        if response.get('ok'):
            return response.get('url')





