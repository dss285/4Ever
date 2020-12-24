import youtube_dl
import json
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
if __name__ == "__main__":
    ytdl_format_options = {
            'format': 'bestaudio/best',
			'outtmpl': 'videos/%(extractor)s-%(id)s-%(title)s.%(ext)s',
			'restrictfilenames': True,
			'nocheckcertificate': True,
			'ignoreerrors': False,
			'logtostderr': False,
			'quiet': True,
			'no_warnings': True,
			'default_search': 'auto',
			'source_address': '0.0.0.0'
	}
    test = "https://www.youtube.com/playlist?list=PLg5_R-wv4gAAOSt50wHPesXlHwKwfYOqG"
    fo = open("test.json", "w")
    with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
        data = ydl.extract_info(test, download=False)
        fo.write(json.dumps(data, sort_keys=True, indent=4))

        fo.write("\n\n\n")
        data2 = ydl.extract_info("https://www.youtube.com/watch?v=JqRxmy1h5as", download=False)
        fo.write(json.dumps(data2, sort_keys=True, indent=4))