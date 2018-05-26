class Message:
    def __init__(self, client, **kwargs):
        self.client = client
        self.channel = self.client.channels.get(kwargs.get('channel'))
        self.user = client.users.get(kwargs.get('user'))
        self.text = kwargs.get('text')
        self.type = kwargs.get('type')
        self.subtype = kwargs.get('subtype')
        self.ts = kwargs.get('ts')
        if self.channel:
            self.channel.register_ts(self.ts)

    def to_format_dict(self):
        return dict(
            user=self.user,
            text=self.text,
            type=self.type,
            subtype=self.subtype,
            ts=self.ts
        )