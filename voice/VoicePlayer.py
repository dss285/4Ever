import discord
import asyncio
import time
import youtube_dl
import os
import glob
import json
import datetime
from collections import deque
from models.EmbedTemplate import EmbedTemplate
class Song:
	def __init__(self, data, title, duration, views, url):
		self.data = data
		self.title = title
		self.duration = duration
		self.views = views
		self.url = url
class VoicePlayer:

	def __init__(self, vc, channel, client):
		self.sounds = {}
		self.update_sounds()
		self.loop = client.loop
		ytdl_format_options = {
			'format': 'bestaudio/best',
			'outtmpl': 'videos/%(extractor)s-%(id)s-%(title)s.%(ext)s',
			'restrictfilenames': True,
			'nocheckcertificate': True,
			'ignoreerrors': True,
			'quiet' : True,
			'logtostderr': False,
			'no_warnings': True,
			'default_search': 'auto',
			'source_address': '0.0.0.0'
		}
		self.ffmpeg_opts = {
			'options' : '-vn',
			'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
		}
		self.ffmpeg_local_opts = {
			'options' : '-vn'
		}
		self.ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
		self.playlist = deque()
		self.looprunning = False
		self.vc = vc
		self.channel = channel
		self.client = client
	def update_sounds(self,):
		sounds = glob.glob('sounds/*')
		for i in sounds:
			self.sounds[os.path.splitext(os.path.basename(i))[0]] = i
	async def playFile(self, fileName):
		while self.vc.is_playing():
			await asyncio.sleep(3)
		self.vc.play(discord.FFmpegPCMAudio(fileName, **self.ffmpeg_local_opts))
	async def handle(self, url):
		if self.vc != None:
			if url:
				await self.add_to_queue(url)
			if not self.looprunning:
				await self.play_loop()
	async def play_loop(self,):
		self.looprunning = True
		while self.playlist:
			song = self.playlist.popleft()
			if song:
				self.vc.play(song.data)
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
				await self.channel.send(embed=EmbedTemplate(title="Song", description="Song skipped"))
	async def resume(self,):
		if self.vc:
			if self.vc.is_paused():
				em = EmbedTemplate(title="Player Resumed",description="pause to pause again")
				self.vc.resume()
				await self.channel.send(embed=em)
	async def add_to_queue(self,url):
		def add_playlist(data, new_songs):
			for x in data['entries']:
				song = Song(discord.FFmpegPCMAudio(x['url'], **self.ffmpeg_opts), x['title'], x['duration'], x['view_count'], x['url'])
				new_songs.append(song)
		data = await self.loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download=False))
		new_songs = []
		if 'entries' in data:
			await self.loop.run_in_executor(None, lambda: add_playlist(data, new_songs))
		else:
			song = Song(discord.FFmpegPCMAudio(data['url'], **self.ffmpeg_opts), data['title'], data['duration'], data.get('view_count'), data.get('url'))

			new_songs.append(song)
		new_songs_str = ""
		for i in new_songs:
			if len(new_songs_str) < 1000:
				new_songs_str += "[{}]({}), {} {:,.0f} views\n".format(i.title[:40], i.url, datetime.timedelta(seconds=i.duration), i.views)
			else:
				break
		self.playlist.extend(new_songs)
		em = EmbedTemplate(title="Added {} to Playlist".format(len(new_songs)),description=new_songs_str)
		await self.channel.send(embed=em)