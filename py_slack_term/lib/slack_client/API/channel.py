from .message import Message


class Channel:
    def __init__(self, client, **kwargs):
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
        self.members = kwargs.get('members')
        self.topic = kwargs.get('topic')
        self.purpose = kwargs.get('purpose')
        self.previous_names = kwargs.get('previous_names')
        self.num_members = kwargs.get('num_members')
        self.last_seen_ts = 0
        self.has_unread = False

    def register_ts(self, ts, *_, as_read=False):
        if float(ts) > float(self.last_seen_ts):
            if as_read:
                self.last_seen_ts = float(ts)
                self.has_unread = False
            else:
                self.has_unread = True
        elif not as_read:
            self.has_unread = False

    def get_info(self):
        response = self.client.slackclient.api_call('channels.info', channel=self.id)
        if response.get('ok'):
            return response.get('group')

    def join(self):
        return self.client.slackclient.api_call('channels.join', channel=self.id)

    def leave(self):
        return self.client.slackclient.api_call('channels.leave', channel=self.id)

    def post_message(self, msg: str, thread_ts=None, reply_broadcast=False):
        # replace @annotated mentions with the corredt escape sequence
        msg.replace('@here', '<!here>')
        msg.replace('@everyone', '<!everyone>')

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
            messages = [Message(self.client, **message) for message in response.get('messages')]
            if len(messages) > 0:
                self.mark(messages[0].ts)
            return messages

    def mark(self, ts):
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