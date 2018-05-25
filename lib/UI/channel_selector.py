import npyscreen


class ChannelSelector(npyscreen.MultiLine):
    def __init__(self, *args, **kwargs):
        super(ChannelSelector, self).__init__(*args, **kwargs)

    def display_value(self, vl):
        return vl.name

    def h_select(self, ch):
        """
        returns the currently selected channel object
        :param ch:
        :return:
        """
        super(ChannelSelector, self).h_select(ch)
        self.parent.select_channel(self.values[self.value])


class BoxedChannelSelector(npyscreen.BoxTitle):
    _contained_widget = ChannelSelector

    def __init__(self, *args, **kwargs):
        self.name = 'Channels'
        super(BoxedChannelSelector, self).__init__(*args, **kwargs)


