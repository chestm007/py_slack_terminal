import logging


class Logger:
    def __init__(self, name: str):
        self.logger = logging.getLogger('py_slack_term')

    def log(self, msg: str) -> None:
        self.logger.debug(str(msg))

