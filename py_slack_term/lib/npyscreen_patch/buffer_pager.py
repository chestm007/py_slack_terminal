import npyscreen
from npyscreen.wgmultiline import MORE_LABEL


class PatchedBufferPager(npyscreen.BufferPager):
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
            # this is the patch     V----------------------------V
            self.setValuesWrap(list(self.display_value(l) for l in self.values))

        if self.center:
            self.centerValues()

        display_length = len(self._my_widgets)
        values_len = len(self.values)

        if self.start_display_at > values_len - display_length:
            self.start_display_at = values_len - display_length
        if self.start_display_at < 0:
            self.start_display_at = 0

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
