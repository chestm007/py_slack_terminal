import time
from typing import Optional, Any

from slack_sdk.errors import SlackApiError

from .message import Message


class Channel:
    def __init__(self, client, kwargs, load_details: bool = False):
        self.client = client
        self.id = kwargs.get('id')
        self.user = kwargs.get('user')
        owner = self.client.users.get(self.user)
        self.name = kwargs.get('name') or (owner.name if owner else self.user or self.id)
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
        self.topic = kwargs.get('topic')
        self.purpose = kwargs.get('purpose')
        self.previous_names = kwargs.get('previous_names')
        self.num_members = kwargs.get('num_members')
        self.last_seen_ts = 0.0
        self.has_unread = False
        self.typing_users = {}
        self.members = {}
        self._details_loaded = False

        if load_details:
            self.load_details()

    def load_details(self) -> None:
        if self._details_loaded:
            return

        try:
            member_ids = self.get_members()
            self.members = {
                u.get_name(): u
                for u in [self.client.users[m] for m in member_ids if m in self.client.users]
            }
        except SlackApiError:
            self.members = {}

        try:
            channel_info = self.get_info()
            last_read = channel_info.get('last_read')
            if last_read:
                self.register_ts(float(last_read), as_read=True)
            unread_count = channel_info.get('unread_count_display')
            if unread_count is None:
                unread_count = channel_info.get('unread_count')
            self.has_unread = bool(unread_count)
        except SlackApiError:
            pass

        self._details_loaded = True

    def register_typing_user(self, user: str) -> None:
        if user in self.client.users:
            self.typing_users[self.client.users[user]] = time.time()

    def register_ts(self, ts: float, *_, as_read: bool = False) -> None:
        if float(ts) >= float(self.last_seen_ts):
            if as_read:
                self.last_seen_ts = float(ts)
                self.has_unread = False
            elif float(ts) > float(self.last_seen_ts) and not as_read:
                self.has_unread = True
        elif not as_read:
            self.has_unread = False

    def get_info(self) -> dict[str, Any]:
        response = self.client.web_client.conversations_info(channel=self.id)
        if response.get('ok'):
            return response.get('channel') or {}
        return {}

    def get_members(self) -> list[str]:
        response = self.client.web_client.conversations_members(channel=self.id)
        if response.get('ok'):
            return response.get('members') or []
        return []

    def join(self) -> dict:
        response = self.client.web_client.conversations_join(channel=self.id)
        if response.get('ok'):
            return response
        return response

    def leave(self) -> dict:
        response = self.client.web_client.conversations_leave(channel=self.id)
        if response.get('ok'):
            return response
        return response

    def post_message(self, msg: str, thread_ts: Optional[float] = None, reply_broadcast: bool = False) -> dict:
        """
        https://api.slack.com/methods/chat.postMessage
        """
        self.load_details()

        for notification in ('here', 'everyone', 'channel'):
            msg = msg.replace('@' + notification, '<!' + notification + '>')

        for name, member in self.members.items():
            if '@' + name + ' ' in msg:
                msg = msg.replace('@' + name, '<@' + member.id + '>')

        return self.client.web_client.chat_postMessage(
            channel=self.id,
            text=msg,
            link_names=True,
            thread_ts=thread_ts,
            reply_broadcast=reply_broadcast
        )

    def post_ephemeral_message(self, msg: str, user: str) -> dict:
        response = self.client.web_client.chat_postEphemeral(
            channel=self.id,
            text=msg,
            user=user
        )
        if response.get('ok'):
            return response
        return response

    def delete_message(self, msg_ts: float) -> dict:
        response = self.client.web_client.chat_delete(
            channel=self.id,
            ts=msg_ts
        )
        if response.get('ok'):
            return response
        return response

    def fetch_messages(self, read: bool = True) -> list[Message]:
        try:
            response = self.client.web_client.conversations_history(
                channel=self.id,
                limit=15
            )
        except SlackApiError as e:
            error = getattr(e.response, 'data', {}).get('error') if getattr(e, 'response', None) else None
            if error == 'not_in_channel':
                return []
            return []

        if response.get('ok'):
            messages = [Message(self.client, **message) for message in response.get('messages', [])]
            if messages and read:
                self.mark(messages[0].ts)
            return messages
        return []

    def mark(self, ts: float) -> None:
        self.client.web_client.conversations_mark(
            channel=self.id,
            ts=ts
        )
