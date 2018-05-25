import json
from threading import Thread

from websocket import create_connection

from lib.logger import Logger


class SlackRTMClient:
    def __init__(self, url, callback):
        self.logger = Logger('SlackRTMClient')
        self.url = url
        self._continue = True
        self.thread = Thread(target=self.event_loop)
        self.ws = None
        self.callback = callback

    def event_loop(self):
        while self._continue:
            try:
                result = self.ws.recv()
                response = json.loads(result)
                self.callback(response)
            except Exception as e:
                self.logger.log(e)
                pass

    def start(self):
        self.ws = create_connection(self.url)
        self._continue = True
        self.thread.start()

    def stop(self):
        self._continue = False
        self.ws.close()
        self.thread.join()