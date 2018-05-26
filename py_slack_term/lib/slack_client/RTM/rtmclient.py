import json

import time
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


class TypingUserWatchdogThread:
    def __init__(self, channel):
        self.channel = channel
        self.interested_widgets = []
        self.thread = threading.Thread(target=self.main_loop)
        self.thread.daemon = True
        self._continue = None
        self.running = False

    def register_interested_widget(self, widget):
        self.interested_widgets.append(widget)

    def main_loop(self):
        while self._continue:
            if self.channel is not None:
                if hasattr(self.channel, 'typing_users'):
                    for t, u in self.channel.typing_users.items():
                        if time.time() > t + 20:
                            del self.channel.typing_users[t]
                            self.channel.typing_user_deleted()
                            for w in self.interested_widgets:
                                w.typing_user_event()
            time.sleep(2)

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
