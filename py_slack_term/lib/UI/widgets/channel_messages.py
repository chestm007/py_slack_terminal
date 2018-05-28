import curses
import re
import threading
import time
import npyscreen

from py_slack_term.lib import Logger
from py_slack_term.lib.npyscreen_patch.buffer_pager import PatchedBufferPager
from ....lib.slack_client.API import Channel, Message


class ChannelMessages(PatchedBufferPager):
    message_format = "{user}: {text}"
    mention_regex = re.compile("<@[A-Z0-9]+>")

    def __init__(self, *args, **kwargs):
        super(ChannelMessages, self).__init__(*args, **kwargs)
        self.autowrap = True

    def display_value(self, vl: Message) -> str:
        if isinstance(vl, Message):
            message_dict = vl.to_format_dict()
            text = str(message_dict.get('text'))
            if text is not None:
                match = re.search(self.mention_regex, text)
                if match:
                    # replace the <@XXXXXX> decorations, and leave only the user id
                    user_id = match.group().replace('<', '').replace('@', '').replace('>', '')
                    # replace userid with an '@' annotated username
                    message_dict['text'] = message_dict.get('text').replace(match.group(),
                                                                        '@' + vl.client.users.get(user_id).get_name())
                text = self.message_format.format(**message_dict)
        # there should only be Message objects passed into here, SOMEHOW we sometimes dont get one
        # or its 'text' attribute is "none"
        # TODO: this is a hack, needs investigation
        else:
            text = str(vl)
        return text

    def set_up_handlers(self):
        super(ChannelMessages, self).set_up_handlers()
        self.handlers.update({
            curses.KEY_LEFT: self.h_exit_left,
            curses.KEY_RIGHT: self.h_exit_right
        })


class BoxedChannelMessages(npyscreen.BoxTitle):
    _contained_widget = ChannelMessages

    def __init__(self, *args, **kwargs):
        self.name = 'Messages'
        super(BoxedChannelMessages, self).__init__(*args, **kwargs)
        self.current_channel = None
        self.typing_user_watchdog_thread = TypingUserWatchdogThread(widget=self)

    def buffer(self, *args, **kwargs) -> None:
        self.entry_widget.buffer(*args, **kwargs)
        self.display()

    def clear_buffer(self, *args, **kwargs) -> None:
        self.entry_widget.clear_buffer(*args, **kwargs)

    def set_channel(self, ch: Channel) -> None:
        """
        function to set title of box to channel name and display associated information
        """
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

    def typing_user_event(self):
        try:
            typing_users = [u.get_name() for u in self.current_channel.typing_users.keys()]
        except:
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
                self.logger.log(e.args)

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