
import asyncio
import discord
import datetime
import pytz
import re
import os
from forever import utilities,database,helper,warframe,voice
from forever.wfmodules import wfmarket,droptables
	# if message.content.startswith(">>owo") or message.content.startswith(key+"owo"):
		
		# 	if message.mentions:
		# 		if client.user in message.mentions:
		# 			responses = ["fucking degenerate"]
		# 			await asyncio.sleep(0.8)
		# 			await message.channel.send(random.choice(responses))	
class Helper:
	def __init__(self,):
		self.dicts = {}
		self.local_tz = pytz.timezone("Europe/Helsinki")
	def utc2local(self, timestamp):
		return datetime.datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc).astimezone(self.local_tz)
	def timestamp2string(self, timestamp, pattern):
		return self.utc2local(timestamp).strftime(pattern)
	def permMessage(self,permname):
		return "(Must have "+permname+" permission)"
	def embedMsg(self,key, extras, module):
		modules = {
			"main" : { 
			"1" : """:gear: **{name}** *{page_n}/{page_max}*\n
				**{key}help** *(main|gfl|moderation|nsfw|voice|warframe)* *(page number, defaults to 1)* - This panel.\n
				**{key}botadmin** *(help)*\n

				**{key}avatar** *target user* - Gets target user's avatar
				**{key}owo** *targetuser (optional)* - OwO someone or yourself.\n
				\n
				**{key}join** *role name* - Join Role\n
				**{key}leave** *role name* - Leave Role\n
				**{key}roles** - Joinable Roles\n
				\n
				**{key}probability** *(trials)* *(successes)* *(chance)* - Calculate probability.\n
				""",
			},
			"nsfw" : {
			"1" : """:peach:**{name}** *{page_n}/{page_max}*\n
				**{key}rule34** *(tags)* - Rule34.xxx API Search\n"""
			},
			"warframe" : { 
			"1" : """:notebook_with_decorative_cover: **{name}** *{page_n}/{page_max}*\n
				**{key}build** *(warframe|primary|secondary|melee|companion)* *(all|list|build's name)* - List shows list of builds available, if you type build's name bot will send you image of it.\n
				**{key}loadout-build *(all|list|build's name)*
				\n
				**{key}frostglobe** *(armormultiplier from mods)* *(extra pwrstr)* *(extra armor, ex. guardian)* - Calculates HP of Frost's Globe.\n
				**{key}reduction-ehp** *(reduction)* *(hp)* - Calculates effective HP based on damage reduction and hp.\n
				**{key}armor-ehp** *(armor)* *(health)* - Calculates effective HP based on armor and HP.\n
				**{key}armor-res** *(armor)* - Calculates damage reduction of armor.\n
				\n
				""",
			"2" : """:notebook_with_decorative_cover: **{name}** *{page_n}/{page_max}*\n
				**{key}relic list** *(axi|neo|meso|lith)* - Provides you with relic list of "Axi" or "Neo" for example.
				**{key}relic show** *(relic name)* - Choose relic's droptable.\n
				**{key}relic worth** *relic name* - Search Warframe.market API for relic's contents. 
				Example: e!relic worth axi v8 relic\n
				\n
				**{key}bounty list** *(cetus|vallis)* - Provides you bounty list of Cetus or Orb Vallis.\n
				**{key}bounty rewards** *(bountyname)* - Choose bounty's droptable\n
				\n
				**{key}price** *itemname* - Search Warframe.market API for item average prices. Relics must be searched like this "Axi V8 Intact"
				Example: e!price ember prime set\n
				\n
				**{key}enemy list** - Sends file of all enemies.\n
				**{key}enemy drops** *(enemy's name)* - Shows you droptable of certain enemy.\n
				\n
				""",
			"3" : """:notebook_with_decorative_cover: **{name}** *{page_n}/{page_max}*\n
				**{key}create message** *{messages}* - {managechannelsperm} Make message for bot to update alerts or Nightwave challenge status.\n
				**{key}create bind** *{binds}* *(role)* - {managechannelsperm} Create bind for the bot's alert or PoE messages.\n
				**{key}remove bind** *{binds}* - {managechannelsperm} Remove bind from the alerts or PoE status.\n
				**{key}bind list** - Lists all possible binds.
				"""
			},
			"voice" : { 
			"1" : """:musical_note: **{name}** *{page_n}/{page_max}*
				**{key}play** *(youtube link)* - Joins the bot and plays the youtube link.
				**{key}pause** - Pauses audio
				**{key}resume** - Resumes audio
				**{key}sounds** - List sounds you can play via typing the words
				"""
			},
			"moderation" : {
			"1" : """:shield: **{name}** *{page_n}/{page_max}*
				**{key}server** - Shows info from the server.{adminperm}\n
				**{key}copy channel** *(from)* *(to)* - Copies one channel into another, currently copy amount is 15 messages. {adminperm}\n
				**{key}empty** *(1-100)* - {managechannelsperm} Message Purge.\n
				\n
				**{key}set log** - Sets log channel into channel where message is sent.{adminperm}\n
				**{key}remove log** Removes current log channel.{adminperm}\n
				\n
				**{key}add role** *(all roles which you wanna add, can add multiple at once)* - Can add roles to joinable roles.{adminperm}\n
				**{key}remove role** *(all roles which you wanna remove, can remove multiple at once)* - Can remove roles from joinable roles.{adminperm}\n
				"""
			},
			"gfl" : {
				"1" : """**{name}** *{page_n}/{page_max}*
				**{key}gfl** *(productiontimers)* *(doll|tdoll|waifu)* *(ar|rf|sg|mg|hg|smg)*
				**{key}gfl** *(productiontimers)* *(eq|equipment)* *(ar|rf|sg|mg|hg|smg)*
				"""
			}
		}
		if module == "main":
			helpdesc = modules[module]["1"].format(key=key,
				adminperm=self.permMessage("Administrator"),
				managechannelsperm=self.permMessage("Manage Channels"),
				messages="("+" | ".join(extras["messages"])+")",
				binds="("+" | ".join(extras["mentions"]["other"])+")",
				name="Main",
				page_n=1,
				page_max=len(modules["main"])
				)
			em = discord.Embed(description=helpdesc, colour=0x8A00E0)
			return em
		else:
			if module.group(2).lower() in modules.keys():
				modulegroups = module
				if module.group(3):
					module = modules[module.group(2)][module.group(3)]
				else:
					module = module.group(2)
					module = modules[module]["1"]
						
				helpdesc = module.format(key=key,
					adminperm=self.permMessage("Administrator"),
					managechannelsperm=self.permMessage("Manage Channels"),
					messages="("+" | ".join(extras["messages"])+")",
					binds="("+" | ".join(extras["mentions"]["other"])+")",
					name=modulegroups.group(2).title(),
					page_n=modulegroups.group(3) if modulegroups.group(3) else 1,
					page_max=len(modules[modulegroups.group(2)])
					)
				em = discord.Embed(description=helpdesc, colour=0x8A00E0)
				return em