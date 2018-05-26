from .lib import Config
from .lib.UI import SlackApplication

from py_slack_term.lib.slack_client.API import SlackApiClient


def main():
    config = Config()
    slackclient = SlackApiClient(config)
    app = SlackApplication(slack_client=slackclient)
    try:
        app.run()
    except KeyboardInterrupt:
        app.stop()
        pass

if __name__ == "__main__":
    main()
