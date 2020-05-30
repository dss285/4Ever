#!/usr/bin/python
import discord
import asyncio
import commands
import config
import time
import re
import datetime
import json
import logging
import pytz
import json
import glob
import os
from forever import utilities, database, helper, warframe, mathBot, voice, dataloop, gfl
from forever.wfmodules import droptables, wfmarket, mentionhandler
class MyClient(discord.Client):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = helper.Helper()
		self.mentionhandler = mentionhandler.MentionHandler()
		self.wfmarket = wfmarket.wfmarket()
		self.droptables = droptables.droptables()
		self.mathbot=mathBot.mathBot()
		self.util=utilities.Utilities()
		self.db = database.Database()
		self.wf = warframe.Warframe(self.db.jsonDict, self.helper)
		self.gfl = gfl.girlsfrontline(self.db.jsonDict)
		self.sounds = {}
		self.vc = {}
		self.wfinfo = None
		self.loopBot = self.loop.create_task(self.loop1())
	async def loop1(self,):
		await self.wait_until_ready()
		while True:
			sounds = glob.glob('sounds/*')
			for i in sounds:
				self.sounds[os.path.splitext(os.path.basename(i))[0]] = i
			try:	
				self.wfinfo = await self.wf.getInfo(self.db.jsonDict)
				await self.util.loop(self, self.wfinfo, self.mentionhandler, self.wf, self.helper, self.db.jsonDict)
			except:
				print("wf module error")
			tmpdel=[]
			for j,k in self.vc.items():
				if len(k.vc.channel.members) ==1:
					await k.leave()
					tmpdel.append(j)
			for i in tmpdel:
				del self.vc[i]
			self.db.saveData()
			await self.mentionhandler.checkAllMentions()
			await asyncio.sleep(30)
	async def on_ready(self):
		print('Logged in as')
		print(discord.__version__)
		print(self.user.name)
		print(self.user.id)
		print('--------------------')
		await client.change_presence(activity=discord.Game(name='e!help'))
# most events expect onmessage for bulk closing
	async def on_raw_message_delete(self,payload):
		message = payload.cached_message
		if message:
			if isinstance(message.channel, discord.abc.GuildChannel):
				if message.author != self.user:
					var = self.db.logChannelCheck(message,self)
					if var != None:
						em = discord.Embed(title="Message Deletion",description="Channel ID: "+str(message.channel.id)+"\nChannel Name:"+message.channel.mention+"\nMember ID: "+str(message.author.id)+"\nMember Name: "+message.author.name+"#"+message.author.discriminator+"\nContent: "+message.content+"\nAttachments:"+str([s.url for s in message.attachments])+"\n",timestamp=datetime.datetime.utcnow())
						em.set_author(name=message.author.name,icon_url=message.author.avatar_url)
						await var.send(embed=em)
		else:
			var = self.db.logChannelCheck(payload.guild_id,self,True)
			if var != None:
				em = discord.Embed(title="Message Deletion",description="Unknown Message Deletion\nChannel ID: "+str(payload.channel_id)+"\nMessage ID:"+str(payload.message_id)+"\nChannel:"+self.get_channel(payload.channel_id).mention,timestamp=datetime.datetime.utcnow())
				em.set_author(name="???",icon_url=self.user.avatar_url)
				await var.send(embed=em)
	async def on_raw_bulk_message_delete(self,payload):
		if len(payload.message_ids) == len(payload.cached_messages):
			messages = payload.cached_messages
			var = self.db.logChannelCheck(messages[0], self)
			if var != None:
				fo = open("/home/dss/data/temp.txt","w+")
				channel = None
				for x in messages:
					channel = x.channel
					fo.write("\nMember ID: "+str(x.author.id)+"\n"+"Member Name: "+x.author.name+"#"+x.author.discriminator+"\nContent: "+x.content+"\nAttachments:"+str([s.url for s in x.attachments])+"\n\n")
				fo.close()
				em = discord.Embed(title="Message Purge",description=str(len(messages))+" messages were deleted in "+channel.mention,timestamp=datetime.datetime.utcnow())
				await var.send(embed=em,file=discord.File("/home/dss/data/temp.txt","temp.txt"))
				os.remove("/home/dss/data/temp.txt")
		else:
			var = self.db.logChannelCheck(payload.guild_id, self, True)
			if var != None:
				ids = "\n".join([str(x) for x in payload.message_ids])
				em = discord.Embed(title="Message Purge",description=str(len(payload.message_ids))+" messages were deleted in "+self.get_channel(payload.channel_id).mention,timestamp=datetime.datetime.utcnow())
				em.add_field(name="Message IDS",value=ids)
				await var.send(embed=em)
	async def on_message_edit(self, before, after):
		if before.author != self.user:
			if before != after:
				var = self.db.logChannelCheck(before, self)
				if var != None:
					try:
						em = discord.Embed(title="Message Edited",description="In "+before.channel.mention,timestamp=datetime.datetime.utcnow())
						em.add_field(name="Before",value=before.content)
						em.add_field(name="After",value=after.content)
						em.set_author(name=before.author.name,icon_url=before.author.avatar_url)
						await var.send(embed=em)
					except:
						pass
	async def on_guild_channel_create(self,channel):
		var = self.db.logChannelCheck(channel, self)
		if var != None:
			em = discord.Embed(title="Channel Created",description="ID:"+str(channel.id)+"\nName:"+channel.name+"\n",timestamp=datetime.datetime.utcnow())
			await var.send(embed=em)
	async def on_guild_channel_delete(self,channel):
		var = self.db.logChannelCheck(channel, self)
		if var != None:
			em = discord.Embed(title="Channel Deleted",description="ID:"+str(channel.id)+"\nName:"+channel.name+"\n",timestamp=datetime.datetime.utcnow())
			await var.send(embed=em)
	async def on_guild_role_create(self, role):
		var = self.db.logChannelCheck(role, self)
		if var != None:
			em = discord.Embed(title="Role Created",description="Role "+role.name+" has been created.")
			await var.send(embed=em)
	async def on_guild_role_delete(self, role):
		var = self.db.logChannelCheck(role, self)
		if var != None:
			em = discord.Embed(title="Role Deleted",description="Role "+role.name+" has been deleted.")
			await var.send(embed=em)
	async def on_member_join(self,member):
		var = self.db.logChannelCheck(member, self)
		if var != None:
			em = discord.Embed(title="Member Joined",description="ID:"+str(member.id),timestamp=datetime.datetime.utcnow())
			em.set_author(name=member.name,icon_url=member.avatar_url)
			await var.send(embed=em)
	async def on_member_remove(self,member):
		var = self.db.logChannelCheck(member, self)
		if var != None:
			em = discord.Embed(title="Member Left/Kicked",description="ID:"+str(member.id),timestamp=datetime.datetime.utcnow())
			em.set_author(name=member.name,icon_url=member.avatar_url)
			await var.send(embed=em)
	async def on_member_update(self, before, after):
		var = self.db.logChannelCheck(before, self)
		if var!= None:
			
			if len(before.roles) != len(after.roles):
				em = discord.Embed(title="Member Updated",timestamp=datetime.datetime.utcnow())
				em.set_author(name=before.name,icon_url=before.avatar_url)
				em.add_field(name="Roles Before:",value="\n".join([str(x) for x  in before.roles]))
				em.add_field(name="Roles After:",value="\n".join([str(x) for x  in after.roles]))
				await var.send(embed=em)
	async def on_member_ban(self,guild,user):
		var = self.db.logChannelCheck(member, self)
		if var != None:
			em = discord.Embed(title="Member Banned",description="ID:"+str(member.id),timestamp=datetime.datetime.utcnow())
			em.set_author(name=member.name,icon_url=member.avatar_url)
			await var.send(embed=em)
# to prevent closing of on message if needed
	async def on_message(self, message):
		#message, client, key, helper, sounds, wf, wfmarket, droptables, mathbot, util, db, botdata, vc
		class_vars = {
			"message" : 	message, 
			"client" : 		self,
			"key" : 		'e!',
			"helper" : 		self.helper,
			"sounds" : 		self.sounds,
			"gfl" :			self.gfl,
			"wf" : 			self.wf,
			"wfmarket" : 	self.wfmarket,
			"droptables" : 	self.droptables,
			"mathbot" : 	self.mathbot,
			"util" : 		self.util,
			"db" : 			self.db,
			"vc" : 			self.vc
		}
		if message.guild:
			await commands.commandRead(class_vars)
		
		if message.author.id in [x["id"] for x in self.db.jsonDict["bot-admins"]]:
			#def modifySolSystem(self, action,i_id, data):
				# 	"nodes": [
    			# 	  {
    			# 	    "name": "neruda",
    			# 	    "node_id": "SolNode221",
    			# 	    "planet_id": 0
    			# 	  },
				# 	"planets": [
      			# 	{
      			# 	  "name": "Mercury",
      			# 	  "planet_id": 0
      			# 	},
			#def modifyBuilds(self, name, action, b_vars=None):
			#def modifyImages(self, subcategory, action, i_id=None, link=None):
			#def modifyBuildImages(self, build, name, action, link=None):
			#def modifyWFItems(self, i_id, action, subcategory, name=None):
			tmp = "e!botadmin"
			if message.content.startswith(tmp):
				if message.content.startswith(tmp+" help"):
					msg = 	"""	{start} help - This\n
								{start} solsystem ({actions}) (planet|node) planetid|name|solnode - Solnode is optional, modifies solsystem database\n
								{start} builds ({actions}) (name){build}\n
								{start} buildimages ({actions}) (warframe|*primary|secondary|melee|companion) (name) (link)\n
								{start} images (add|remove) ({categories}) (link)\n
								{start} dicts ({actions}) (nightwave|items|missions|sorties) (key) (value)\n
								{start} listkeys \[key1, key2...\] - Keys how far you want to go.\n
							""".format(start=tmp, 
										build="\{key : value\} - Keys are companion, description, primary, secondary, melee",
										categories="|".join(self.db.jsonDict["images"].keys()),
										actions="add|edit|remove").replace("(","(*").replace(")","*)")
					em = discord.Embed(title="Bot admin help", description=msg)
					await message.channel.send(embed=em)
				if message.content.startswith(tmp+" solsystem"):
					#e!botadmin solsystem (planet|node) (planet_id|name|planet_id)
					reg = re.match(tmp+"\ssolsystem\s(add|edit|remove)\s(planet|node)\s(\d*)\|([a-zA-Z]*)[\|]?([a-zA-Z0-9]*)?", message.content)
					if reg:
						data = {}
						data["vars"] = {}
						action = reg.group(1)
						which = reg.group(2)
						planetid = reg.group(3)
						name = reg.group(4)
						solnode = reg.group(5) if reg.group(5) else None
						#data["vars"]
						#data["which"]
						data["which"] = which
						data["vars"]["name"] = name
						data["vars"]["planet_id"] = planetid

						tolook = [x[which+"_id"] for x in self.db.jsonDict["solsystem"][which+"s"]]
						index = None
						if solnode:
							data["vars"]["node_id"] = solnode
							try:
								index = tolook.index(solnode)
							except ValueError:
								index = None
								await message.add_reaction("❌")
						else:
							try:
								index = tolook.index(planetid)
							except ValueError:
								index = None
								await message.add_reaction("❌")
						if self.db.modifySolSystem(action, index, data):
							await message.add_reaction("☑️")
						else:
							await message.add_reaction("❌")
				if message.content.startswith(tmp+" builds"):
					#def modifyBuilds(self, name, action, b_vars=None):
					#{
     				# 	"companion": "adarza",
    				# 	"description": "3",
    				# 	"melee": "sarpa",
    				# 	"primary": "lanka",
    				# 	"secondary": "catchmoon"
					#}
					#e!botadmin builds (action) (name) (vars)?
					reg = re.match(tmp+"\sbuilds\s(add|edit|remove)\s(\S*)\s?(\{.*\})?", message.content)
					if reg:
						action = reg.group(1)
						name = reg.group(2)
						b_Vars = reg.group(3) if reg.group(3) else None
						if b_Vars != None:
							b_vars = json.loads(b_vars)
						if b_vars != None and (action =="edit" or action=="add"):
							if self.db.modifyBuilds(action, name, b_vars):
								await message.add_reaction("☑️")
							else:
								await message.add_reaction("❌")
						elif b_vars == None and action == "remove":
							if self.db.modifyBuilds(action, name, b_vars):
								await message.add_reaction("☑️")
							else:
								await message.add_reaction("❌")	
				if message.content.startswith(tmp+" buildimages"):
					#def modifyBuildImages(self, build, name, action, link=None):
					#e!botadmin buildimages (action) (name) (link)?
					reg = re.match(tmp+" buildimages\s(add|edit|remove)\s(warframe|primary|secondary|melee|companion)\s([A-Za-z]*)\s?(http[s]?:\/\/.+[\/]\S*)?", message.content)
					if reg:
						action = reg.group(1)
						buildtype = reg.group(2)
						name = reg.group(3)
						link = reg.group(4) if reg.group(4) else None
						if (action in ["add", "edit"] and link) or action=="remove":
							self.db.modifyBuildImages(buildtype, name, action, link)
							await message.add_reaction("☑️")
						else:
							await message.add_reaction("❌")
				if message.content.startswith(tmp+" images"):
					#def modifyImages(self, subcategory, action, i_id=None, link=None):
					#e!botadmin images (action) (category) (link)
					#http[s]?:\/\/(.*)\/?[\/]?(.*)?
					reg = re.match(tmp+"\simages\s(add|remove)\s(\S*)\s(http[s]?:\/\/.+[\/]\S*)", message.content)
					if reg:
						action = reg.group(1)
						category = reg.group(2)
						idn = reg.group(3)
						if idn in self.db.jsonDict["images"]:
							if action =="remove":
								index = self.db.jsonDict["images"][category].index(idn)
								if self.db.modifyImages(category, action, index, None):
									await message.add_reaction("☑️")
								else:
									await message.add_reaction("❌")
						else:
							if action == "add":
								if self.db.modifyImages(category, action, None, idn):
									await message.add_reaction("☑️")
								else:
									await message.add_reaction("❌")
				if message.content.startswith(tmp+" dicts"):
					#def modifyDicts(self, action, subcategory, i_id, name=None):
					#e!botadmin wfdicts (action) (category) (key) (value)
					#categories
						#nightwave
						#items
						#missions
						#sorties
					reg = re.match(tmp+"\sdicts\s(add|edit|remove)\s(nightwave|items|missions|sorties)\s(\S*)\s?(.*)?", message.content)
					if reg:
						action = reg.group(1)
						category = reg.group(2)
						ikey = reg.group(3)
						ivalue = reg.group(4) if reg.group(4) else None

						if category in self.db.jsonDict:
							if self.db.modifyDicts(action, category, ikey, ivalue):
								await message.add_reaction("☑️")
							else:
								await message.add_reaction("❌")
				if message.content.startswith(tmp+" listkeys"):
					reg = re.match(tmp+" listkeys\s?(\[.*\])", message.content)
					if reg:
						load = json.loads(reg.group(1))
						length = len(load)
						msg = self.db.jsonDict
						for i in load:
							msg = msg[i]
						msg = "\n".join(msg)
						em = discord.Embed(title="Key List", description=msg)
						await message.channel.send(embed=em)

client = MyClient()
client.run(config.bot_token)

