import curses

import npyscreen


class ScreenLogger(npyscreen.BufferPager):
    def __init__(self, *args, **kwargs):
        super(ScreenLogger, self).__init__(*args, **kwargs)
        self.autowrap = True

    def set_up_handlers(self):
        super(ScreenLogger, self).set_up_handlers()
        self.handlers.update({
            curses.KEY_LEFT: self.h_exit_left,
            curses.KEY_RIGHT: self.h_exit_right
        })


class BoxedScreenLogger(npyscreen.BoxTitle):
    _contained_widget = ScreenLogger

    def __init__(self, *args, **kwargs):
        self.name = "Debug"
        super(BoxedScreenLogger, self).__init__(*args, **kwargs)

    def log(self, msg):
        self.entry_widget.buffer([str(msg)])
        self.display()