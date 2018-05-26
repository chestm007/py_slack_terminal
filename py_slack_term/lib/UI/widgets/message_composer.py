import curses

import npyscreen


class MessageComposer(npyscreen.MultiLineEdit):
    def __init__(self, *args, **kwargs):
        super(MessageComposer, self).__init__(*args, **kwargs)

    def set_up_handlers(self):
        super(MessageComposer, self).set_up_handlers()
        self.handlers.update({
            curses.KEY_ENTER: self.h_enter,
            curses.ascii.LF: self.h_enter
        })

    def h_enter(self, *args):
        self.parent.send_message()


class BoxedMessageComposer(npyscreen.BoxTitle):
    _contained_widget = MessageComposer

    def __init__(self, *args, **kwargs):
        self.name = 'Message'
        super(BoxedMessageComposer, self).__init__(*args, **kwargs)

    def clear_message(self):
        self.entry_widget.value = ''
