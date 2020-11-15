class Playlist():
    def __init__(self, loopable=True):
        self.queue = []
        self.loopable = loopable
        self.current = None
    def add(self, song):
        if song.url not in [x.url for x in self.queue]:
            self.queue.append(song)
    def returnOne(self,):
        if self.queue:
            return self.queue.pop(0)
