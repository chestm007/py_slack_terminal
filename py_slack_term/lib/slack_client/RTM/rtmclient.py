import json

import time
import websocket
import threading

from py_slack_term.lib import Logger


class SlackRTMClient:
    def __init__(self, slack_client, callback):
        self.slack_client = slack_client
        self.callback = callback
        self.logger = Logger(' ')
        self.ws = None
        self.wst = None

    def start(self):
        self.logger.log('starting RTM client')
        self.url = None
        while not self.url:
            self.url = self.slack_client.rtm_connect()
            if not self.url:
                self.logger.log('error getting RealTimeMessaging URL. waiting 5 seconds...')
                time.sleep(5)

        self.ws = websocket.WebSocketApp(self.url, on_message=self.on_message, on_error=self.on_error)
        self.wst = threading.Thread(target=self.ws.run_forever)
        self.wst.daemon = True
        self.wst.start()
        self.logger.log('started RTM client')

    def on_message(self, _, message):
        data = json.loads(message)
        self.callback(data)

    def on_error(self, *args):
        self.logger.log(args)
        self.stop()
        self.start()

    def stop(self):
        self.logger.log('closing RTM client')
        if hasattr(self, 'ws'):
            self.ws.close(timeout=1)
            del self.ws
        if hasattr(self, 'wst'):
            del self.wst
        self.logger.log('closed RTM client')


class TypingUserWatchdogThread:
    def __init__(self, widget):
        self.widget = widget
        self.thread = threading.Thread(target=self.main_loop)
        self.thread.daemon = True
        self._continue = None
        self.running = False
        self.logger = Logger('')

    def main_loop(self):
        while self._continue:
            try:
                if self.widget.current_channel is not None:
                    if hasattr(self.widget.current_channel, 'typing_users'):
                        if self.widget.current_channel.typing_users is not None:
                            prev_len = len(self.widget.current_channel.typing_users.keys())
                            self.widget.current_channel.typing_users = {
                                u: t for u, t in self.widget.current_channel.typing_users.items() if time.time() < t + 20
                            }
                            if len(self.widget.current_channel.typing_users.keys()) < prev_len:
                                self.widget.typing_user_event()
                time.sleep(2)
            except Exception as e:
                self.logger.log(e.args)

    def start(self):
        if not self.running:
            self._continue = True
            self.thread.start()
            self.running = True

    def stop(self):
        if self.running:
            self._continue = False
            self.thread.join(timeout=3)
            self.running = False
