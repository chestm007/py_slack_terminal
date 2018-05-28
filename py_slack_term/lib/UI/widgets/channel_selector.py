import curses

import npyscreen

from ....lib.slack_client.API import Channel


class ChannelSelector(npyscreen.MultiLine):
    """
    selected channel colour is set as "BOLD"
    """
    def __init__(self, *args, **kwargs):
        super(ChannelSelector, self).__init__(*args, **kwargs)

    def display_value(self, vl: Channel) -> str:
        prefix = '*' if vl.has_unread else ' '
        if vl.is_private:
            prefix += ' <>'
        elif vl.is_channel:
            prefix += '  #'
        else:
            prefix += '  @'
        return prefix + vl.name

    def h_select(self, ch) -> None:
        """
        returns the currently selected channel object
        :param ch:
        :return:
        """
        super(ChannelSelector, self).h_select(ch)
        self.parent.select_channel(self.values[self.value])

    def set_up_handlers(self):
        super(ChannelSelector, self).set_up_handlers()
        self.handlers.update({
            curses.KEY_RIGHT: self.h_exit_right,
            curses.KEY_LEFT: self.h_exit_left
        })


class BoxedChannelSelector(npyscreen.BoxTitle):
    _contained_widget = ChannelSelector

    def __init__(self, *args, **kwargs):
        self.name = 'Channels'
        super(BoxedChannelSelector, self).__init__(*args, **kwargs)

    def update_channels(self, in_channels) -> None:
        self.values = in_channels
