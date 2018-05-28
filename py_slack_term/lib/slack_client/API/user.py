class User:
    ADMIN_USER_PREFIX = ''
    PREFER_REAL_NAME = False

    def __init__(self, kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.display_name = kwargs.get('profile').get('display_name_normalized')
        self.real_name = kwargs.get('profile').get('real_name_normalized')
        self.is_admin = kwargs.get('is_admin')

    def get_name(self) -> str:
        if self.PREFER_REAL_NAME:
            name = self.real_name or self.display_name
        else:
            name = self.display_name or self.real_name
        return (self.ADMIN_USER_PREFIX if self.is_admin else '') + name

    def __str__(self) -> str:
        return self.get_name()
