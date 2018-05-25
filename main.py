from lib.UI.main import SlackApplication
from lib.config import Config
from lib.slack_client.client import SlackApiClient

config = Config()
slackclient = SlackApiClient(config)
app = SlackApplication(slack_client=slackclient)
try:
    app.run()
except KeyboardInterrupt:
    app.stop()
    pass
