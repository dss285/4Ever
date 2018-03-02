import MySQLdb
import asyncio
import discord
import urllib
import urllib.request
from classes import database
from PIL import Image
class Main:
	def __init__(self,host,user,passwd,dbn):
		self.db = database.Database(host,user,passwd,dbn)
		self.conn = self.db.conn
		self.nsfwchannels=[]
		self.adminRole=[]
	def nsfwchannel(self, message, client, key):
		msg = message.content[len(key+'nsfw'):].strip()
		if msg.startswith('add'):
			print('s')
			sql = "INSERT INTO nsfwchannels (channel_id, serverid) VALUES (%s, %s)"
			args = (message.channel.id, message.server.id)
			self.db.insert(sql, args)
		elif msg.startswith('remove'):
			print('s1')
			sql = "DELETE FROM nsfwchannels WHERE channel_id=%s"
			args = (int(message.channel.id),)
			delete(self.conn, sql, args)
	def insertInto(self,nsfwchannels,adminrole):
		self.nsfwchannels = nsfwchannels
		self.adminRole = adminrole
