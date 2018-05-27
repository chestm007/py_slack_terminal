import pprint

import time

from py_slack_term.lib import Config
from py_slack_term.lib.slack_client.API import SlackApiClient
from py_slack_term.lib.slack_client.RTM import SlackRTMClient

if __name__ == '__main__':
    """
    this is just a dummy testing stub. not executed when ran from cli
    """

    print = pprint.pprint
    config = Config()
    client = SlackApiClient(config)

    #client.refresh_channel_list()
    #print(client.channels)
    #print([m.text for m in client.channels['admin'].fetch_messages()])

    #client.refresh_user_list()
    #print(client.users)

    rtm_client = SlackRTMClient(client, print)
    rtm_client.start()
    while True:
        time.sleep(10)
        pass

