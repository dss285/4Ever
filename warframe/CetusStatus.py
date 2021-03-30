import time
class CetusStatus:
    def __init__(self, expiry):
        self.expiry = expiry
        self.start = self.expiry-150*60
    def isNight(self,):
        if self.minutes_left() <= 50:
            return True
        else:
            return False
    def seconds_left(self):
        return self.expiry-time.time()
    def minutes_left(self,):
        return self.seconds_left()//60
    def __str__(self,):
        return "Night" if self.isNight() else "Day"

