import MySQLdb
import asyncio
import discord
from classes import database
class Main:
	def __init__(self,host,user,passwd,dbn):
		self.db = database.Database(host,user,passwd,dbn)
		self.conn = self.db.conn
		self.dicts = {}
	def showdic(self,):
		print(self.dicts)
	def isAdmin(self,message):
		if self.dicts[message.server.id]["adminrid"] in message.author.roles:
			return True
		else:
			return False
	def roles(self,message):
		lst = []
		for i in message.author.roles:
			lst.append(i.id)
		return lst
	def channels(self, c):
		lst = []
		print(c)
		for i in c:
			lst.append(i[0])
		print(lst)
		return lst
	def nsfwchannel(self, message, key):
		msg = message.content[len(key+'nsfw'):].strip()
		if self.dicts[message.server.id]["adminrid"] in self.roles(message):
			if msg.startswith('add'):
				c = self.conn.cursor()
				sql = "SELECT COUNT(*) FROM nsfwchannels WHERE channel_id=%s"
				args = (message.channel.id,)
				c.execute(sql,args)
				var = c.fetchone()
				if not var[0]>0:
					sql = "INSERT INTO nsfwchannels (channel_id, serverid) VALUES (%s, %s)"
					args = (message.channel.id, message.server.id)
					self.db.insert(sql, args)
					return True
				else:
					return False
			elif msg.startswith('remove'):
				sql = "DELETE FROM nsfwchannels WHERE channel_id=%s"
				args = (int(message.channel.id),)
				self.db.delete(sql, args)
				return True
	def adminRole(self, message, key):
		if message.author == message.server.owner:
			if len(message.role_mentions) == 1:
				role = message.role_mentions[0].id
				sql = "INSERT INTO server(admin_role,serverid) VALUES (%s,%s) ON DUPLICATE KEY UPDATE admin_role=%s"
				args = (role, message.server.id ,role)
				self.db.insert(sql,args)
				return True
			else:
				return False
	def isnsfw(self, message):
		for key,value in self.dicts.items():
			if key==message.server.id:
				nsfwchannels = value["nsfwchannels"]
				for i in nsfwchannels:
					if message.channel.id == i:
						return True
		return False
	def isServerIn(self,server):
		if server in self.dicts.keys():
			return True
		else:
			return False
	async def createMessage(self, client, message, key):
		if self.dicts[message.server.id]["adminrid"] in self.roles(message):
			msg = message.content.split(" ") 
			msg = msg[len(msg)-1]
			
			savemsg = ""
			channel = message.channel
			if msg == "poe":
				savemsg = await client.send_message(channel, "Placeholder for PoE Status")
			elif msg == "alerts":
				savemsg = await client.send_message(channel, "Placeholder for Alerts")
			else:
				await client.send_message(channel,"Something went wrong")
				return False
			if isinstance(savemsg, discord.Message):
				sql = "INSERT INTO alertmessages VALUES (%s,%s,%s,%s)"
				args = (message.channel.id, message.server.id, savemsg.id, msg)
				self.db.insert(sql,args)
				return True
		else:
			return False

