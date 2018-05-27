import npyscreen

from py_slack_term.lib.UI.forms import SlackConversationsWindowForm


class SlackApplication(npyscreen.NPSAppManaged):
    def __init__(self, *args, slack_client=None, config=None, **kwargs):
        npyscreen.NPSAppManaged.STARTING_FORM = 'conversations_window'

        self.slack_client = slack_client
        self.config = config

        super(SlackApplication, self).__init__(*args, **kwargs)

        self.conversations_window = None

    def onStart(self):
        self.conversations_window = self.addForm('conversations_window',
                                                 SlackConversationsWindowForm,
                                                 name='Slack Terminal',
                                                 slack_client=self.slack_client,
                                                 config=self.config)

    def stop(self):
        self.conversations_window.stop()