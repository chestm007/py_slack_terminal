import npyscreen
from ...lib import Logger
from ...lib.UI.widgets import BoxedChannelMessages
from ...lib.UI.widgets import BoxedChannelSelector
from ...lib.UI.widgets import BoxedMessageComposer
from ...lib.slack_client.API import Message

from py_slack_term.lib.slack_client.RTM import SlackRTMClient


class SlackWindowForm(npyscreen.FormBaseNew):
    def __init__(self, *args, slack_client=None, **kwargs):
        self.logger = Logger('SlackWindowForm')
        self.slack_client = slack_client
        rtm_url = self.slack_client.rtm_connect()
        super(SlackWindowForm, self).__init__(*args, **kwargs)
        self.channel_selector = None
        self.current_channel = None

        self.rtm_client = SlackRTMClient(rtm_url, self.new_RTM_event)
        self.rtm_client.start()

    def create(self):
        y, x = self.useable_space()

        self.channel_selector = self.add_widget(BoxedChannelSelector, max_width=x // 5)
        self.channel_messages = self.add_widget(BoxedChannelMessages,
                                                relx=self.channel_selector.width + 3,
                                                rely=self.channel_selector.rely,
                                                max_height=y-8)  # type: BoxedChannelMessages
        self.message_composer = self.add_widget(BoxedMessageComposer, relx=self.channel_messages.relx, rely=y-6, max_height=4)

        self.refresh_channels()

    def select_channel(self, ch):
        self.current_channel = ch
        self.channel_messages.clear_buffer()
        self.channel_messages.buffer(list(reversed(ch.fetch_messages())))
        self.channel_messages.set_channel(ch)
        self.current_channel.has_unread = False
        self.channel_messages.display()

    def refresh_channels(self):
        self.channel_selector.update_channels(self.slack_client.get_active_channels_im_in())
        self.channel_selector.display()

    def send_message(self):
        message = self.message_composer.value
        self.message_composer.clear_message()
        self.current_channel.post_message(msg=message)

    def new_RTM_event(self, event: dict):

        event_type = event.get('type')
        if event_type == 'message':
            message = Message(self.slack_client, **event)
            if self.current_channel:
                if event.get('channel') == str(self.current_channel.id):
                    self.channel_messages.buffer([message])
                    self.current_channel.mark(message.ts)
                self.current_channel.has_unread = False
        self.display()
        self.channel_messages.display()

    def stop(self):
        self.rtm_client.stop()


class SlackApplication(npyscreen.NPSAppManaged):
    def __init__(self, *args, slack_client=None, **kwargs):
        self.slack_client = slack_client
        super(SlackApplication, self).__init__(*args, **kwargs)

    def onStart(self):
        self.main_window = self.addForm('MAIN', SlackWindowForm, name='Slack Terminal', slack_client=self.slack_client)

    def stop(self):
        self.main_window.stop()