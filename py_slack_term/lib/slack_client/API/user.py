class User:
    def __init__(self, kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.display_name = kwargs.get('profile').get('display_name_normalized')
        self.real_name = kwargs.get('profile').get('real_name_normalized')
        self.is_admin = kwargs.get('is_admin')

    def get_name(self):
        return ('[ADMIN]' if self.is_admin else '') + (self.display_name or self.real_name)

    def __str__(self):
        return self.get_name()