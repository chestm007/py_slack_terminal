import pkg_resources

from .lib import Config
from .lib.UI import SlackApplication

from py_slack_term.lib.slack_client.API import SlackApiClient

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--version', action='store_true')
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()


def main():
    debug = False
    if args.version:
        version = pkg_resources.get_distribution("py_slack_term").version
        print("\nVersion: py_slack_term: {}".format(version))
        return
    if args.debug:
        debug = True
    config = Config()
    if debug:
        config.debug = True
    slackclient = SlackApiClient(config)
    app = SlackApplication(slack_client=slackclient, config=config)
    try:
        app.run()
    except KeyboardInterrupt:
        app.stop()
        pass

if __name__ == "__main__":
    main()
