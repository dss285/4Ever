class NightwaveItem:
    def __init__(self, start_time, expiry_time, name, daily=False):
        self.start_time = start_time
        self.expiry_time = expiry_time
        self.name = name
        self.daily = daily
