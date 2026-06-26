import curses
import re
import threading
import time
import npyscreen
from datetime import datetime

from py_slack_term.lib import Logger
from py_slack_term.lib.npyscreen_patch.buffer_pager import PatchedBufferPager
from ....lib.slack_client.API import Channel, Message


class ChannelMessages(PatchedBufferPager):
    mention_regex = re.compile("<@[A-Z0-9]+>")

    def __init__(self, *args, **kwargs):
        super(ChannelMessages, self).__init__(*args, **kwargs)
        self.autowrap = True

    def display_value(self, vl: Message) -> str:
        if isinstance(vl, Message):
            message_dict = vl.to_format_dict()
            text = str(message_dict.get('text') or '')
            if text:
                match = re.search(self.mention_regex, text)
                if match:
                    user_id = match.group().replace('<', '').replace('@', '').replace('>', '')
                    user = vl.client.users.get(user_id)
                    if user:
                        message_dict['text'] = text.replace(match.group(), '@' + user.get_name())
                message_format = f"[{datetime.fromtimestamp(float(message_dict.get('ts') or 0)):%d/%m-%H:%M}] {message_dict.get('user')}: {message_dict.get('text')}"
                text = message_format
        else:
            text = str(vl)
        return text

    def set_up_handlers(self):
        super(ChannelMessages, self).set_up_handlers()
        self.handlers.update({
            curses.KEY_LEFT: self.h_exit_left,
            curses.KEY_RIGHT: self.h_exit_right,
            ord('q'): self.quit_app,
        })

    def quit_app(self, *args):
        self.parent.parent.quit_app()


class BoxedChannelMessages(npyscreen.BoxTitle):
    _contained_widget = ChannelMessages

    def __init__(self, *args, **kwargs):
        self.name = 'Messages'
        super(BoxedChannelMessages, self).__init__(*args, **kwargs)
        self.current_channel = None
        self.typing_user_watchdog_thread = TypingUserWatchdogThread(widget=self)
        self.message_watchdog_thread = MessageWatchdogThread(widget=self)

    def buffer(self, *args, **kwargs) -> None:
        self.entry_widget.buffer(*args, **kwargs)
        self.display()

    def clear_buffer(self, *args, **kwargs) -> None:
        self.entry_widget.clear_buffer(*args, **kwargs)

    def set_channel(self, ch: Channel) -> None:
        if ch is not None:
            self.current_channel = ch

        new_name = "Messages | {name}".format(name=ch.name)

        if ch.topic:
            topic = ch.topic.get('value')
        elif ch.purpose:
            topic = ch.purpose.get('value')
        else:
            topic = None
        if topic:
            new_name += " ({})".format(topic)

        if ch.is_private:
            new_name += " [PRIVATE]"

        self.name = new_name
        self.typing_user_watchdog_thread.start()
        self.message_watchdog_thread.set_channel(ch)
        self.message_watchdog_thread.start()

    def typing_user_event(self):
        try:
            typing_users = [u.get_name() for u in self.current_channel.typing_users.keys()]
        except Exception:
            typing_users = []

        if len(typing_users) < 1:
            self.footer = None
        elif len(typing_users) == 1:
            self.footer = '{} is typing...'.format(typing_users[0])
        elif len(typing_users) < 4:
            self.footer = '{} and {} are typing...'.format(', '.join(typing_users[:-1]), typing_users[-1])
        elif len(typing_users) >= 4:
            self.footer = 'Multiple people are typing...'
        self.display()

    def destroy(self):
        self.typing_user_watchdog_thread.stop()
        self.message_watchdog_thread.stop()
        super(BoxedChannelMessages, self).destroy()


class TypingUserWatchdogThread:
    def __init__(self, widget):
        self.widget = widget
        self.thread = threading.Thread(target=self.main_loop)
        self.thread.daemon = True
        self._continue = None
        self.running = False
        self.logger = Logger('')

    def main_loop(self):
        while self._continue:
            try:
                if self.widget.current_channel is not None:
                    if hasattr(self.widget.current_channel, 'typing_users'):
                        if self.widget.current_channel.typing_users is not None:
                            prev_len = len(self.widget.current_channel.typing_users.keys())
                            self.widget.current_channel.typing_users = {
                                u: t for u, t in self.widget.current_channel.typing_users.items() if time.time() < t + 5
                            }
                            if len(self.widget.current_channel.typing_users.keys()) < prev_len:
                                self.widget.typing_user_event()
                time.sleep(2)
            except Exception as e:
                self.logger.log(str(e))

    def start(self):
        if not self.running:
            self._continue = True
            self.thread.start()
            self.running = True

    def stop(self):
        if self.running:
            self._continue = False
            self.thread.join(timeout=3)
            self.running = False


class MessageWatchdogThread:
    def __init__(self, widget, poll_interval: float = 3.0):
        self.widget = widget
        self.thread = threading.Thread(target=self.main_loop)
        self.thread.daemon = True
        self._continue = None
        self.running = False
        self.poll_interval = poll_interval
        self.logger = Logger('')
        self._last_delivered_ts = 0.0
        self._active_channel_id = None

    def set_channel(self, channel: Channel) -> None:
        self._active_channel_id = channel.id if channel else None
        self._last_delivered_ts = float(channel.last_seen_ts or 0) if channel else 0.0

    def _as_float_ts(self, value) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    def main_loop(self):
        while self._continue:
            try:
                current_channel = self.widget.current_channel
                if current_channel is not None:
                    if self._active_channel_id != current_channel.id:
                        self.set_channel(current_channel)

                    messages = current_channel.fetch_messages(read=False)
                    if messages:
                        newest_seen = self._last_delivered_ts
                        new_messages = []
                        for message in reversed(messages):
                            ts_value = self._as_float_ts(message.ts)
                            if ts_value > self._last_delivered_ts:
                                new_messages.append(message)
                                if ts_value > newest_seen:
                                    newest_seen = ts_value
                        if new_messages:
                            self.widget.buffer(new_messages)
                            self._last_delivered_ts = newest_seen
                            if self.widget.parent and hasattr(self.widget.parent, 'channel_selector') and self.widget.parent.channel_selector:
                                self.widget.parent.channel_selector.display()
                time.sleep(self.poll_interval)
            except Exception as e:
                self.logger.log(str(e))
                time.sleep(self.poll_interval)

    def start(self):
        if not self.running:
            self._continue = True
            self.thread.start()
            self.running = True

    def stop(self):
        if self.running:
            self._continue = False
            self.thread.join(timeout=3)
            self.running = False
