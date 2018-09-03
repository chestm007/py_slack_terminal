import asyncio
import pprint

import time
from concurrent.futures.thread import ThreadPoolExecutor

from slackclient.channel import Channel

from py_slack_term.lib import Config
from py_slack_term.lib.slack_client.API import SlackApiClient
from py_slack_term.lib.slack_client.RTM import SlackRTMClient


class DummyLogger:
    def log(self, msg):
        pprint.pprint(msg)


if __name__ == '__main__':
    starttime = time.time()
    """
    this is just a dummy testing stub. not executed when ran from cli
    """

    print = pprint.pprint

    config = Config()

    client = SlackApiClient(config)

    def api_test():
        pass
        #print(client.channels)
        #print([m.text for m in client.channels['admin'].fetch_messages()])

        #client.refresh_user_list()
        #print(client.users)
        for channel in client.channels.values():
            if channel.name == 'shitzngiggles':
                while True:
                    print(channel.post_message('@chris laptops?'))
                    time.sleep(3)

    def rtm_test():
        rtm_client = SlackRTMClient(client, print)
        rtm_client.logger = DummyLogger()
        rtm_client.start()
        while True:
            time.sleep(10)
            pass

    api_test()
    endtime = time.time()
    print(endtime - starttime)

