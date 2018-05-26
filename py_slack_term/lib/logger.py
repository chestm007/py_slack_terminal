class Logger:
    def __init__(self, name):
        self.name = name

    def log(self, msg):
        print('{}: {}'.format(self.name,msg))