import discord
import asyncio
import time
import youtube_dl
import os
import glob
import datetime
from voice.Playlist import Playlist
from voice.Song import Song
from abstract.EmbedTemplate import EmbedTemplate
class VoicePlayer:
	def __init__(self, vc, channel, client):
		self.sounds = {}
		self.updateSounds()
		ytdl_format_options = {
			'format': 'bestaudio/best',
			'outtmpl': 'videos/%(extractor)s-%(id)s-%(title)s.%(ext)s',
			'restrictfilenames': True,
			'noplaylist': True,
			'nocheckcertificate': True,
			'ignoreerrors': False,
			'logtostderr': False,
			'quiet': True,
			'no_warnings': True,
			'default_search': 'auto',
			'source_address': '0.0.0.0'
		}
		self.ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
		self.playlist = Playlist(False)
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
			await self.playSong()		
	async def playSong(self,):
		while self.vc.is_playing():
			await asyncio.sleep(2)
		else:
			song = self.playlist.returnOne()
			if song:
				self.vc.play(discord.FFmpegPCMAudio(song.voice))
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
		song_info = self.ytdl.extract_info(url, download=True)
		em = EmbedTemplate(title="Added to Playlist",description="Added song "+song_info["title"]+" to playlist")
		data = self.ytdl.prepare_filename(song_info)
		data = {
			"title" : song_info["title"],
			"duration" : song_info["duration"],
			"views" : song_info["view_count"],
			"song" : data
		}
		self.playlist.add(Song(data["duration"], data["views"], data["title"], url, data["song"]))
		await self.channel.send(embed=em)