import os
import yaml


class Config:
    def __init__(self):
        with open(os.path.expanduser('~') + '/.config/py_slack_term/config.yml') as config_file:
            config = yaml.load(config_file)
        self.token = config.get('slacktoken')

