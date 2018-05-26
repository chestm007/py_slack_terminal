import os
import yaml


class Config:
    config_path = os.path.expanduser('~') + '/.config/py_slack_term/'
    config_filename = 'config.yml'

    def __init__(self):
        if not os.path.exists(self.config_path):
            os.mkdir(self.config_path)
        if not os.path.isfile(self.config_path + self.config_filename):
            with open(self.config_path + self.config_filename, 'w+') as config_file:
                config = dict(
                    slacktoken=input("Please paste your slack API token: ")
                )
                config_file.write(yaml.dump(config))

        with open(self.config_path + self.config_filename) as config_file:
            config = yaml.load(config_file)
        self.token = config.get('slacktoken')

