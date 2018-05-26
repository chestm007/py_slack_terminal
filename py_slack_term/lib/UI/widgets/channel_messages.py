import re

import npyscreen

from ....lib.slack_client.API import Channel, Message


class ChannelMessages(npyscreen.BufferPager):
    message_format = "{user}: {text}"
    mention_regex = re.compile("<@[A-Z0-9]+>")

    def __init__(self, *args, **kwargs):
        super(ChannelMessages, self).__init__(*args, **kwargs)
        self.editable = False
        self.autowrap = True

    def display_value(self, vl: Message) -> str:
        if isinstance(vl, Message):
            message_dict = vl.to_format_dict()
            try:
                text = str(message_dict.get('text'))
            except:
                pass
            if text:
                match = re.search(self.mention_regex, text)
                if match:
                    user_id = match.group().replace('<', '').replace('@', '').replace('>', '')
                    message_dict['text'] = message_dict.get('text').replace(match.group(),
                                                                        '@' + vl.client.users.get(user_id).get_name())
                return self.message_format.format(**message_dict)
        return vl

    def display(self, *args, **kwargs):
        super(ChannelMessages, self).display(*args, **kwargs)

    def clear_buffer(self, *args, **kwargs):
        """
        compatibility with non pythonic code in library
        """
        self.clearBuffer(*args, **kwargs)

    # TODO: this is a monkey patch of the base class Pager
    # TODO: this method can be removed when https://github.com/npcole/npyscreen/pull/60 is merged
    def update(self, clear=True):
        #we look this up a lot. Let's have it here.
        if self.autowrap:
            self.setValuesWrap(list(self.display_value(l) for l in self.values))

        if self.center:
            self.centerValues()

        display_length = len(self._my_widgets)
        values_len = len(self.values)

        if self.start_display_at > values_len - display_length:
            self.start_display_at = values_len - display_length
        if self.start_display_at < 0: self.start_display_at = 0

        indexer = 0 + self.start_display_at
        for line in self._my_widgets[:-1]:
            self._print_line(line, indexer)
            indexer += 1

        # Now do the final line
        line = self._my_widgets[-1]

        if values_len <= indexer+1:
            self._print_line(line, indexer)
        else:
            line.value = MORE_LABEL
            line.highlight = False
            line.show_bold = False

        for w in self._my_widgets:
            # call update to avoid needless refreshes
            w.update(clear=True)
        # There is a bug somewhere that affects the first line.  This cures it.
        # Without this line, the first line inherits the color of the form when not editing. Not clear why.
        self._my_widgets[0].update()


class BoxedChannelMessages(npyscreen.BoxTitle):
    _contained_widget = ChannelMessages

    def __init__(self, *args, **kwargs):
        self.name = 'Messages'
        super(BoxedChannelMessages, self).__init__(*args, **kwargs)

    def buffer(self, *args, **kwargs) -> None:
        self.entry_widget.buffer(*args, **kwargs)

    def clear_buffer(self, *args, **kwargs) -> None:
        self.entry_widget.clear_buffer(*args, **kwargs)

    def set_channel(self, ch: Channel) -> None:
        """
        function to set title of box to channel name and display associated information
        """
        new_name = "Messages | {name}".format(name=ch.name)

        if ch.topic:
            topic = ch.topic.get('value')
        elif ch.purpose:
            topic = ch.purpose.get('value')
        else:
            topic = None
        if topic:
            new_name += " ({})".format(topic)

        if ch.is_private:
            new_name += " [PRIVATE]"

        self.name = new_name


