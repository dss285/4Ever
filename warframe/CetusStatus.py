import time
class CetusStatus:
    def __init__(self, expiry):
        self.expiry = expiry
        self.start = self.expiry-150*60
    def isNight(self,):
        if self.minutesLeft() <= 50:
            return True
        else:
            return False
    def minutesLeft(self,):
        return ((self.expiry-time.time())//60)
    def __str__(self,):
        return "Night" if self.isNight() else "Day"

