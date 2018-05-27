import logging

class Logger:
    def __init__(self, name):
        self.logger = logging.getLogger('py_slack_term')

    def log(self, msg):
        self.logger.debug(str(msg))

