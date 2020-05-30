import discord
import asyncio
import time
import youtube_dl
import datetime
class Voice:
	def __init__(self, vc, channel):
		ytdl_format_options = {
			'format': 'bestaudio/best',
			'outtmpl': 'videos/%(extractor)s-%(id)s-%(title)s.%(ext)s',
			'restrictfilenames': True,
			'noplaylist': True,
			'nocheckcertificate': True,
			'ignoreerrors': True,
			'logtostderr': False,
			'quiet': True,
			'no_warnings': False,
			'default_search': 'auto',
			'source_address': '0.0.0.0'
		}
		self.ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
		self.playlist = []
		self.current = None
		self.vc = vc
		self.channel = channel
	def playVoice(self,):
		if self.vc != None:
			if not self.vc.is_playing():
				if self.playlist:
					self.current = self.playlist[0]
					self.vc.play(self.playlist[0]["song"], after=lambda e: print("error:%s" %e)if e else self.afterPlay())
				else:
					if self.current != None:
						self.current = None
	def afterPlay(self,):
		del self.playlist[0]
		if self.playlist:
			self.playVoice()
	async def playFile(self,fileName):
		if self.vc != None:
			if not self.vc.is_playing():
				self.vc.play(discord.FFmpegPCMAudio(fileName))
	async def currentSong(self,):
		em = discord.Embed(title=self.current["title"],timestamp=datetime.datetime.utcnow())
		em.add_field(name="Duration", value=str(time.strftime('%H:%M:%S',time.gmtime(self.current["duration"]))))
		em.add_field(name="Views",value=str(self.current["views"])+" views")
		await self.channel.send(embed=em)
	async def leave(self,):
		if self.vc != None:
			if self.vc.is_connected():
				em = discord.Embed(title="Left Voice Channel",description="Bot has left voice channel")
				await self.vc.disconnect()
				await self.channel.send(embed=em)
	async def pause(self,):
		if self.vc != None:
			if self.vc.is_playing():
				em = discord.Embed(title="Player Paused",description="Type e!resume to continue playing")
				self.vc.pause()
				await self.channel.send(embed=em)
	async def skip(self,):
		if self.vc  != None:
			if self.vc.is_playing():
				self.vc.stop()
				em = discord.Embed(title="Song Skipped",description="Song was skipped")
				await self.channel.send(embed=em)
				del self.playlist[0]
				if self.playlist:
					self.playVoice()
	async def resume(self,):
		if self.vc != None:
			if self.vc.is_paused():
				em = discord.Embed(title="Player Resumed",description="Type e!pause to pause again")
				self.vc.resume()
				await self.channel.send(embed=em)
	async def addtoPlaylist(self,url):
		song_info = self.ytdl.extract_info(url, download=True)
		em = discord.Embed(title="Added to Playlist",description="Added song "+song_info["title"]+" to playlist")
		data = self.ytdl.prepare_filename(song_info)
		url = {
			"title" : song_info["title"],
			"duration" : song_info["duration"],
			"views" : song_info["view_count"],
			"song" : discord.FFmpegPCMAudio(data)
		}
		self.playlist.append(url)
		await self.channel.send(embed=em)
		await asyncio.sleep(1)
		if not self.vc.is_playing():
			self.playVoice()
	async def show_playlist(self,):
		count = 1
		strings = []
		if self.current != None:
			strings.append("**Currently playing:** "+self.current["title"]+", Views:"+str(self.current["views"])+", Duration:*"+str(time.strftime('%H:%M:%S',time.gmtime(self.current["duration"])))+"*\n")
		for i in self.playlist:
			strings.append("**"+str(count)+".** "+i["title"]+", Views:"+str(i["views"])+", Duration:*"+str(time.strftime('%H:%M:%S',time.gmtime(i["duration"])))+"*\n")
			count += 1
		em = discord.Embed(title="Playlist",description="\n".join(strings))
		await self.channel.send(embed=em)
		

	