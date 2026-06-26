from typing import Any, List, Optional, cast

import npyscreen

from py_slack_term.lib.slack_client.API import User


class SearchTitleText(npyscreen.TitleText):
    def __init__(self, *args, on_change=None, **kwargs):
        self._on_change = on_change
        super().__init__(*args, **kwargs)

    def when_value_edited(self):
        if self._on_change:
            self._on_change(self.value)


class UserList(npyscreen.MultiLineAction):
    def __init__(self, *args, on_select=None, **kwargs):
        self._on_select = on_select
        super().__init__(*args, **kwargs)

    def display_value(self, vl: User) -> str:
        return UserPickerPopup._display_user(vl)

    def actionHighlighted(self, act_on_this, key_press):
        if self._on_select:
            self._on_select(act_on_this)


class UserPickerPopup(npyscreen.ActionPopupWide):
    DEFAULT_LINES = 24
    DEFAULT_COLUMNS = 80
    SHOW_ATX = 0
    SHOW_ATY = 0

    def __init__(self, *args, users: List[User], **kwargs):
        self._all_users = list(users)
        self._filtered_users = list(users)
        self.value: Optional[User] = None
        self.search_box = None
        self.user_list = None
        super().__init__(*args, **kwargs)

    @staticmethod
    def _display_user(user: User) -> str:
        name = user.get_name() if hasattr(user, 'get_name') else getattr(user, 'name', 'unknown')
        real = getattr(user, 'real_name', None)
        display = getattr(user, 'display_name', None)
        label_bits = [name]
        if display and display != name:
            label_bits.append(f'@{display}')
        if real and real not in (display, name):
            label_bits.append(real)
        return ' — '.join(label_bits)

    def create(self):
        self.add(npyscreen.FixedText, value='Type to filter, arrows to choose, Enter to confirm', editable=False)
        self.search_box = self.add(
            SearchTitleText,
            name='Search',
            value='',
            begin_entry_at=10,
            on_change=self._filter_users,
            height=2,
            max_height=2,
        )
        self.user_list = self.add(
            UserList,
            name='Users',
            values=[],
            height=14,
            max_height=14,
            scroll_exit=True,
            on_select=self._choose_user,
        )
        self._filter_users('')

    def _filter_users(self, query: str):
        query = (query or '').strip().lower()
        if not query:
            self._filtered_users = list(self._all_users)
        else:
            self._filtered_users = [
                user for user in self._all_users
                if query in user.id.lower()
                or query in user.name.lower()
                or query in (user.display_name or '').lower()
                or query in (user.real_name or '').lower()
                or query in self._display_user(user).lower()
            ]

        user_list = cast(Any, self.user_list)
        user_list.values = self._filtered_users
        user_list.cursor_line = 0 if self._filtered_users else 0
        user_list.display()

    def _choose_user(self, user):
        self.value = user
        self.editing = False

    def on_ok(self):
        if self._filtered_users:
            idx = min(max(getattr(self.user_list, 'cursor_line', 0), 0), len(self._filtered_users) - 1)
            self.value = self._filtered_users[idx]
        else:
            self.value = None
        self.editing = False

    def on_cancel(self):
        self.value = None
        self.editing = False
