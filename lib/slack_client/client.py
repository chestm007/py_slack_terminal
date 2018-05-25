import pprint

from slackclient import SlackClient
from lib.config import Config



class Client:
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
        channels = self.get_active_channels()
        self.channels = {str(c.id): c for c in channels}
        private_channels = self.get_my_channels(_type=self.PRIVATE)
        self.channels.update({str(c.id): c for c in private_channels})

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



class Channel:
    def __init__(self, client, **kwargs):
        self.client = client
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.is_channel = kwargs.get('is_channel')
        self.created = kwargs.get('created')
        self.is_archived = kwargs.get('is_archived')
        self.is_general = kwargs.get('is_general')
        self.unlinked = kwargs.get('unlinked')
        self.creator = kwargs.get('creator')
        self.name_normalized = kwargs.get('name_normalized')
        self.is_shared = kwargs.get('is_shared')
        self.is_org_shared = kwargs.get('is_org_shared')
        self.is_member = kwargs.get('is_member')
        self.is_private = kwargs.get('is_private')
        self.is_mpim = kwargs.get('is_mpim')
        self.members = kwargs.get('members')
        self.topic = kwargs.get('topic')
        self.purpose = kwargs.get('purpose')
        self.previous_names = kwargs.get('previous_names')
        self.num_members = kwargs.get('num_members')

    def get_info(self):
        return self.client.slackclient.api_call('channels.info', channel=self.id)

    def join(self):
        return self.client.slackclient.api_call('channels.join', channel=self.id)

    def leave(self):
        return self.client.slackclient.api_call('channels.leave', channel=self.id)

    def post_message(self, msg: str, thread_ts=None, reply_broadcast=False):
        return self.client.slackclient.api_call('chat.postMessage',
                                         channel=self.id,
                                         text=msg,
                                         as_user=True,
                                         thread_ts=thread_ts,
                                         reply_broadcast=reply_broadcast)

    def post_ephemeral_message(self, msg:str, user: str):
        return self.client.slackclient.api_call('chat.postEphemeral',
                                         channel=self.id,
                                         text=msg,
                                         user=user)

    def delete_message(self, msg_ts):
        return self.client.slackclient.api_call('chat.delete',
                                         channel=self.id,
                                         ts=msg_ts)

    def fetch_messages(self):
        response = self.client.slackclient.api_call('conversations.history',
                                             channel=self.id,
                                             count=200)
        if response.get('ok'):
            return [Message(self.client, **message) for message in response.get('messages')]

    def mark(self, ts):
        self.client.slackclient.api_call('channels.mark',
                                         channel=self.id,
                                         ts=ts)


class Message:
    def __init__(self, client, **kwargs):
        self.client = client
        self.user = client.users.get(kwargs.get('user'))
        self.text = kwargs.get('text')
        self.type = kwargs.get('type')
        self.subtype = kwargs.get('subtype')
        self.ts = kwargs.get('ts')

    def to_format_dict(self):
        return dict(
            user=self.user,
            text=self.text,
            type=self.type,
            subtype=self.subtype,
            ts=self.ts
        )


class User:
    def __init__(self, kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.display_name = kwargs.get('profile').get('display_name_normalized')
        self.real_name = kwargs.get('profile').get('real_name_normalized')
        self.is_admin = kwargs.get('is_admin')

    def get_name(self):
        return ('[ADMIN]' if self.is_admin else '') + (self.display_name or self.real_name)

    def __str__(self):
        return self.get_name()


if __name__ == '__main__':
    config = Config()
    client = Client(config)

    #client.refresh_channel_list()
    #print(client.channels)
    #print([m.text for m in client.channels['admin'].fetch_messages()])

    #client.refresh_user_list()
    #print(client.users)
    client.refresh_channel_list()
    pprint.pprint(list(client.channels.values()))
