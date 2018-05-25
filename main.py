from lib.UI.main import SlackApplication
from lib.config import Config
from lib.slack_client.client import Client

config = Config()
slackclient = Client(config)
app = SlackApplication(slack_client=slackclient)
app.run()