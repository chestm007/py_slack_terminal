import npyscreen


class ScreenLogger(npyscreen.BufferPager):
    def __init__(self, *args, **kwargs):
        super(ScreenLogger, self).__init__(*args, **kwargs)
        self.autowrap = True


class BoxedScreenLogger(npyscreen.BoxTitle):
    _contained_widget = ScreenLogger

    def __init__(self, *args, **kwargs):
        self.name = "Debug"
        super(BoxedScreenLogger, self).__init__(*args, **kwargs)

    def log(self, msg):
        self.entry_widget.buffer([str(msg)])
        self.display()