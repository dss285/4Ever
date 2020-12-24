import discord
import asyncio
import time
import youtube_dl
import os
import glob
import datetime
from abstract.EmbedTemplate import EmbedTemplate
class VoicePlayer:
	def __init__(self, vc, channel, client):
		self.sounds = {}
		self.updateSounds()
		ytdl_format_options = {
			'format': 'bestaudio/best',
			'outtmpl': 'videos/%(extractor)s-%(id)s-%(title)s.%(ext)s',
			'restrictfilenames': True,
			'nocheckcertificate': True,
			'ignoreerrors': False,
			'quiet' : True,
			'logtostderr': False,
			'no_warnings': True,
			'default_search': 'auto',
			'source_address': '0.0.0.0'
		}
		self.ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
		self.playlist = []
		self.looprunning = False
		self.vc = vc
		self.channel = channel
		self.client = client
	def updateSounds(self,):
		sounds = glob.glob('sounds/*')
		for i in sounds:
			self.sounds[os.path.splitext(os.path.basename(i))[0]] = i
	async def playFile(self, fileName):
		while self.vc.is_playing():
			await asyncio.sleep(3)
		self.vc.play(discord.FFmpegPCMAudio(fileName))
	async def handle(self, url):
		if self.vc != None:
			if url:
				await self.addtoPlaylist(url)
			if not self.looprunning:
				await self.playLoop()
	async def playLoop(self,):
		self.looprunning = True
		while self.playlist:
			song = self.playlist.pop(0)
			if song:
				self.vc.play(song["data"])
			while self.vc.is_playing():
				await asyncio.sleep(2)
		self.looprunning = False
	async def pause(self,):
		if self.vc:
			if self.vc.is_playing():
				em = EmbedTemplate(title="Player Paused",description="resume to continue playing")
				self.vc.pause()
				await self.channel.send(embed=em)
	async def skip(self,):
		if self.vc:
			if self.vc.is_playing():
				self.vc.stop()
				await self.channel.send(embed=EmbedTemplate(title="Song", value="Song skipped"))
	async def resume(self,):
		if self.vc:
			if self.vc.is_paused():
				em = EmbedTemplate(title="Player Resumed",description="pause to pause again")
				self.vc.resume()
				await self.channel.send(embed=em)
	async def addtoPlaylist(self,url):
		data = self.ytdl.extract_info(url, download=False)
		added = []
		if 'entries' in data:
			for x in data['entries']:
				
				filename = x['url']
				song = {
					"data" 		: discord.FFmpegPCMAudio(filename),
					"title" 	: x["title"],
					"duration" 	: x["duration"],
					"views" 	: x["view_count"],
				}
				self.playlist.append(song)
				added.append({
					"title" : x["title"],
					"duration" 	: x["duration"],
					"views" 	: x["view_count"],
					"url" : 	x["webpage_url"]
					})
				
		else:
			filename = data['url']
			song = {
				"data" 		: discord.FFmpegPCMAudio(filename),
				"title" 	: data["title"],
				"duration" 	: data["duration"],
				"views" 	: data["view_count"],
			}
			self.playlist.append(song)
			added.append({
				"title" :  data["title"],
				"duration" 	: data["duration"],
				"views" 	: data["view_count"],
				"url" : 	data["webpage_url"]
			})
		addedstr = ""
		for i in added:
			if len(addedstr) < 1000:
				addedstr += "[{}]({}), {} {:,} views\n".format(i["title"][:40], i["url"], datetime.timedelta(seconds=i["duration"]), i["views"])
			else:
				break
		em = EmbedTemplate(title="Added {} to Playlist".format(len(added)),description=addedstr)
		await self.channel.send(embed=em)