import os
import yaml


class Config:
    config_path = os.path.expanduser('~') + '/.config/py_slack_term/'
    config_filename = 'config.yml'

    def __init__(self):
        if not os.path.exists(self.config_path):
            os.mkdir(self.config_path)
        if not os.path.isfile(self.config_path + self.config_filename):
            print("Welcome to py_slack_term!")
            print("Get your tokens from: https://api.slack.com/apps")
            print("Authorize the app for a user and copy that User OAuth Token (usually xoxp-...)")
            print("If using Socket Mode, also copy your App-Level Token (xapp-...)")
            print()
            user_token = input("User OAuth Token (xoxp-...): ").strip()
            app_token = input("App-Level Token for Socket Mode (xapp-..., optional): ").strip()
            config = dict(
                slacktoken=user_token,
                socket_mode_token=app_token if app_token else None
            )
            with open(self.config_path + self.config_filename, 'w') as config_file:
                yaml.dump(config, config_file)

        with open(self.config_path + self.config_filename) as config_file:
            config = yaml.safe_load(config_file) or {}
        self.token: str = config.get('slacktoken')
        self.socket_mode_token: str = config.get('socket_mode_token')
        self.debug: bool = True if config.get('debug') else False
