import collections
import npyscreen


class BufferPager(npyscreen.Pager):
    def __init__(self, screen, maxlen=None, *args, **keywords):
        super(BufferPager, self).__init__(screen, *args, **keywords)
        self.values = collections.deque(maxlen=maxlen)

    def clear_buffer(self):
        self.values.clear()

    def buffer(self, lines, scroll_end=True, scroll_if_editing=False):
        "Add data to be displayed in the buffer."
        self.values.extend(lines)
        if scroll_end:
            if not self.editing:
                self.start_display_at = len(self.values) - len(self._my_widgets)
            elif scroll_if_editing:
                self.start_display_at = len(self.values) - len(self._my_widgets)