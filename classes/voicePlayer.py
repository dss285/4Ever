import asyncio
import discord
import youtube_dl
import time

class voicePlayer:
	def __init__(self,server):
		self.server = server
		self.playlist = []
		self.playing = False
		self.current = []
		self.voice = None
	def addToPlaylist(self,url):
		self.playlist.append(url)
	def isItPlaying(self,):
		if self.playing == True:
			return true
		else:
			return false
	async def disconnect(self,):
		self.voice.disconnect()
	def test(self,):
		print(self.playlist)
	def getPlaylist(self,):
		return self.playlist
	def addPlaylist(self,url):
		ytdl = youtube_dl.YoutubeDL({'outputtmpl':'%(id)s%(ext)s','quiet':True,})
		with ytdl:
			result = ytdl.extract_info(url, download=False)
			print(result.get("url",None))

	async def player(self,client=None,message=None,yt=True,song=None):
		if self.playing == False:
			if yt == True:
				playerM = await self.voice.create_ytdl_player(self.playlist[0])
			else:
				playerM = self.voice.create_ffmpeg_player(song)
			playerM.volume = 0.6
			self.current = [playerM.title,playerM.duration] if yt else None
			if yt == True:
				await client.send_message(message.channel,"**Currently playing: **"+str(self.current[0])+"**\nDuration: **"+str(time.strftime('%H:%M:%S',time.gmtime(self.current[1]))))
			playerM.start()
			self.playing = True
			while not playerM.is_done():
				await asyncio.sleep(1)
			else:
				self.playing = False
				if yt == True:
					self.playlist.remove(self.playlist[0])
					if self.playlist:
						await self.player(client, message)
					else:
						await self.voice.disconnect()
				else:
					await self.voice.disconnect()
	async def join(self, message, client):
		channel = message.author.voice.voice_channel
		server = message.author.server
		if not client.is_voice_connected(server):
			try:
				self.voice = await client.join_voice_channel(channel)
				await client.wait_until_ready()
			except:
				print("error")
		else:
			try:
				await self.voice.move_to(message.author.voice.voice_channel)
				await client.wait_until_ready()
			except:
				print("ok")
	async def playVoice(self, song):
		await self.player(None,None,False,song)
