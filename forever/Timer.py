import time
class Timer:
    def __init__(self, expiry):
        self.expiry = expiry
    def isExpired(self,):
        if self.expiry <= time.time():
            return True
        else:
            return False