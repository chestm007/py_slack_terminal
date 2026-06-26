# Python Slack Terminal #
[![CircleCI](https://circleci.com/gh/chestm007/py_slack_terminal.svg?style=svg)](https://circleci.com/gh/chestm007/py_slack_terminal)  

## install ##
```
$ pip install py_slack_terminal
```

## running ##

```
$ slack-term
```

## shortcuts ##

While focused on the channel list:
- `n` creates a new public channel
- `c` starts a new DM
- `d` leaves the selected channel
- `q` closes the app

## authentication ##

On first launch, you'll be prompted for your Slack User OAuth Token (`xoxp-...`).
If you want real-time events, also enter your App-Level Token (`xapp-...`) for Socket Mode.

The config is saved in `~/.config/py_slack_term/config.yml`.

Alternatively, create the config manually:

```
slacktoken: <bot token here>
socket_mode_token: <app-level token here>
```
