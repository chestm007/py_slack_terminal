import pkg_resources

from .lib import Config
from .lib.UI import SlackApplication

from py_slack_term.lib.slack_client.API import SlackApiClient

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--version', action='store_true')
args = parser.parse_args()


def main():
    if args.version:
        version = pkg_resources.get_distribution("py_slack_term").version
        print("\nVersion: py_slack_term: {}".format(version))
    else:
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
