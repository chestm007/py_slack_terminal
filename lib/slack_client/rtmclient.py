import json

import websocket
import threading


class SlackRTMClient:
    def __init__(self, url, callback):
        self.callback = callback
        self.ws = websocket.WebSocketApp(url, on_message=self.on_message)
        self.wst = threading.Thread(target=self.ws.run_forever)
        self.wst.daemon = True

    def start(self):
        self.wst.start()

    def on_message(self, _, message):
        data = json.loads(message)
        self.callback(data)

    def stop(self):
        self.ws.close()
        self.wst.join(timeout=10)


