import time

from .message import Message


class Channel:
    def __init__(self, client, kwargs):
        self.client = client
        self.id = kwargs.get('id')
        self.name = kwargs.get('name') or self.client.users.get(kwargs.get('user')).name
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
        self.members = {u.get_name(): u for u in [self.client.users[m] for m in self.get_members()]}
        self.topic = kwargs.get('topic')
        self.purpose = kwargs.get('purpose')
        self.previous_names = kwargs.get('previous_names')
        self.num_members = kwargs.get('num_members')
        self.last_seen_ts = 0
        self.has_unread = True
        messages = self.fetch_messages(read=False)
        try:
            self.last_seen_ts = float(messages[0].ts)
        except IndexError:
            pass

        channel_info = self.get_info()
        last_read = channel_info.get('last_read')
        if last_read:
            self.register_ts(last_read, as_read=True)
        self.typing_users = {}

    def register_typing_user(self, user: str) -> None:
        self.typing_users[self.client.users[user]] = time.time()

    def register_ts(self, ts: float, *_, as_read: bool=False) -> None:
        if float(ts) >= float(self.last_seen_ts):
            if as_read:
                self.last_seen_ts = float(ts)
                self.has_unread = False
            elif float(ts) > float(self.last_seen_ts) and not as_read:
                self.has_unread = True
        elif not as_read:
            self.has_unread = False

    def get_info(self) -> dict:
        response = self.client.slackclient.api_call('conversations.info', channel=self.id)
        if response.get('ok'):
            return response.get('channel')

    def get_members(self) -> dict:
        response = self.client.slackclient.api_call('conversations.members', channel=self.id)
        if response.get('ok'):
            return response.get('members')

    def join(self) -> dict:
        response = self.client.slackclient.api_call('channels.join', channel=self.id)
        if response.get('ok'):
            return response

    def leave(self) -> dict:
        response = self.client.slackclient.api_call('conversations.leave', channel=self.id)
        if response.get('ok'):
            return response

    def post_message(self, msg: str, thread_ts: float=None, reply_broadcast: bool=False) -> dict:
        """
        https://api.slack.com/methods/chat.postMessage
        """
        # replace @annotated mentions with the correct escape sequence
        for notification in ('here', 'everyone', 'channel'):
            msg = msg.replace('@' + notification, '<!' + notification + '>')

        # replace @annotated user mentions with <@USERID> sequence
        for name, member in self.members.items():
            if '@' + name + ' ' in msg:
                msg = msg.replace('@' + name, '<@' + member.id + '>')

        return self.client.slackclient.api_call('chat.postMessage',
                                                channel=self.id,
                                                text=msg,
                                                link_names=True,
                                                as_user=True,
                                                thread_ts=thread_ts,
                                                reply_broadcast=reply_broadcast)

    def post_ephemeral_message(self, msg:str, user: str) -> dict:
        response = self.client.slackclient.api_call('chat.postEphemeral',
                                                channel=self.id,
                                                text=msg,
                                                user=user)
        if response.get('ok'):
            return response

    def delete_message(self, msg_ts: float) -> dict:
        response = self.client.slackclient.api_call('chat.delete',
                                                channel=self.id,
                                                ts=msg_ts)
        if response.get('ok'):
            return response

    def fetch_messages(self, read: bool=True) -> list:
        response = self.client.slackclient.api_call('conversations.history',
                                                    channel=self.id,
                                                    count=200)
        if response.get('ok'):
            messages = [Message(self.client, **message) for message in response.get('messages')]
            if len(messages) > 0:
                if read:
                    self.mark(messages[0].ts)
            return messages

    def mark(self, ts: float) -> None:
        if self.is_mpim:
            endpoint = 'mpim'
        elif self.is_private:
            endpoint = 'groups'
        elif self.is_channel:
            endpoint = 'channels'
        else:
            endpoint = 'im'
        self.client.slackclient.api_call(endpoint + '.mark',
                                         channel=self.id,
                                         ts=ts)
