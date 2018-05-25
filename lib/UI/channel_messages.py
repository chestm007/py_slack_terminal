import npyscreen
import re

from lib.UI.helpers.buffer_pager import BufferPager


class ChannelMessages(BufferPager):
    message_format = "{user}: {text}"
    mention_regex = re.compile("<@[A-Z0-9]+>")

    def __init__(self, *args, **kwargs):
        super(ChannelMessages, self).__init__(*args, **kwargs)
        self.editable = False

    def display_value(self, vl):
        message_dict = vl.to_format_dict()
        match = re.search(self.mention_regex, message_dict.get('text'))
        if match:
            user_id = match.group().replace('<', '').replace('@', '').replace('>', '')
            message_dict['text'] = message_dict.get('text').replace(match.group(),
                                                                    '@' + vl.client.users.get(user_id).get_name())
        return self.message_format.format(**message_dict)

    def display(self, *args, **kwargs):
        super(ChannelMessages, self).display(*args, **kwargs)


class BoxedChannelMessages(npyscreen.BoxTitle):
    _contained_widget = ChannelMessages

    def __init__(self, *args, **kwargs):
        self.name = 'Messages'
        super(BoxedChannelMessages, self).__init__(*args, **kwargs)

    def buffer(self, *args, **kwargs):
        self.entry_widget.buffer(*args, **kwargs)

    def clear_buffer(self, *args, **kwargs):
        self.entry_widget.clear_buffer(*args, **kwargs)

    def set_channel(self, ch):
        new_name = "Messages | {name}".format(name=ch.name)

        purpose = ch.purpose.get('value')
        if purpose:
            new_name += " ({})".format(purpose)

        if ch.is_private:
            new_name += " [PRIVATE]"

        self.name = new_name

