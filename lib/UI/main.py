import npyscreen

from lib.UI.channel_messages import BoxedChannelMessages
from lib.UI.channel_selector import BoxedChannelSelector
from lib.UI.message_composer import BoxedMessageComposer


class SlackWindowForm(npyscreen.FormBaseNew):
    def __init__(self, *args, slack_client=None, **kwargs):
        self.slack_client = slack_client
        super(SlackWindowForm, self).__init__(*args, **kwargs)
        self.channel_selector = None
        self.current_channel = None

    def create(self):
        y, x = self.useable_space()
        self.channel_selector = self.add_widget(BoxedChannelSelector, max_width=x // 5)
        self.channel_messages = self.add_widget(BoxedChannelMessages,
                                                relx=self.channel_selector.width + 3,
                                                rely=self.channel_selector.rely,
                                                max_height=y-8)
        self.message_composer = self.add_widget(BoxedMessageComposer, relx=self.channel_messages.relx, rely=y-6, max_height=4)
        self.refresh_channels()

    def select_channel(self, ch):
        self.current_channel = ch
        self.channel_messages.clear_buffer()
        self.channel_messages.buffer(list(reversed(ch.fetch_messages())))
        self.channel_messages.set_channel(ch)
        self.channel_messages.display()

    def refresh_channels(self):
        self.channel_selector.values = self.slack_client.get_active_channels_im_in()

    def send_message(self):
        message = self.message_composer.value
        self.message_composer.clear_message()
        self.current_channel.post_message(msg=message)



class SlackApplication(npyscreen.NPSAppManaged):
    def __init__(self, *args, slack_client=None, **kwargs):
        self.slack_client = slack_client
        super(SlackApplication, self).__init__(*args, **kwargs)

    def onStart(self):
        self.addForm('MAIN', SlackWindowForm, name='Slack Terminal', slack_client=self.slack_client)
