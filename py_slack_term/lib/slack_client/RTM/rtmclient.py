import json
import threading
import time
import websocket

from py_slack_term.lib import Logger


class SlackRTMClient:
    def __init__(self, slack_client, callback):
        self.slack_client = slack_client
        self.callback: classmethod = callback
        self.logger = Logger(' ')
        self.url: str = None
        self.ws: websocket.WebSocketApp = None
        self.wst: threading.Thread = None

    def start(self) -> None:
        self.logger.log('starting RTM client')
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

    def on_message(self, _, message: str) -> None:
        data = json.loads(message)
        self.callback(data)

    def on_error(self, *args: list) -> None:
        self.logger.log(args)
        self.stop()
        self.start()

    def stop(self) -> None:
        self.logger.log('closing RTM client')
        if hasattr(self, 'ws'):
            self.ws.close(timeout=1)
            del self.ws
        if hasattr(self, 'wst'):
            del self.wst
        if hasattr(self, 'url'):
            self.url = None
        self.logger.log('closed RTM client')
