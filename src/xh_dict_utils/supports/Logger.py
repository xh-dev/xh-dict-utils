class Logger(object):
    def __init__(self, channel: list):
        self.channels = channel

    def write(self, message):
        for channel in self.channels:
            channel.write(message)

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass
