#!/usr/bin/python
import discord
import asyncio
import aiohttp
import urllib.request
import xml.etree.ElementTree as ET
import random
import youtube_dl
import re
import glob
import json
from classes import utilities,image,database,main,completionists

from PIL import ImageFilter
from PIL import ImageFile
from PIL import Image
global sounds
sounds = glob.glob('sounds/*')


ImageFile.LOAD_TRUNCATED_IMAGES = True
global voice
voice = None
async def commandRead(message, client, key, functions, conn, voiceplayers, util=utilities.Utilities()):
	global sounds
	if "!e " in message.content:
		if util.CommandPreTest(message,'help',key):
			helpdesc =""":question:** Help**

				:gear:** Commands**
				!help - This panel


				:musical_note:** Voice Related**
				!play (URL) - Plays youtube URL
				!sounds - List all kinds of random sounds that you can type


				:peach:** NSFW Related**
				!rule34 - Rule34 API Search
				!real - Realbooru API Search
				"""
			await client.send_message(message.channel,helpdesc)
		if util.CommandPreTest(message,'sounds',key):
			string = "**Sounds:**\n"
			for i in sounds:
				sv = re.search(r'(sounds)\/(.*).(mp3|ogx)',i)
				string += str(sv.group(2)+"\n")
				print(string)
			await client.send_message(message.channel,string)
####	#########################################ADMIN FUNCTIONS##################################################		

		if util.CommandPreTest(message,'empty',key):
			if functions.isAdmin(message) or message.author == message.server.owner:
				amountsOfDel = message.content[len(key+'empty'):].strip()
				amountsOfDel = int(amountsOfDel+1)
				deleted = await client.purge_from(message.channel, limit=amountsOfDel)
		if util.CommandPreTest(message,'nsfw',key):
			if functions.isAdmin(message) or message.author == message.server.owner:
				if functions.nsfwchannel(message, key):
					await client.send_message(message.channel, "Updated channel!")
		if util.CommandPreTest(message,'admrole',key):
			if message.author == message.server.owner:
				returned = functions.adminRole(message, key)
				if returned:
					await client.send_message(message.channel, "Role has been updated")
				else:
					await client.send_message(message.channel, "Something went wrong")
		if util.CommandPreTest(message,'createmsg',key):
			if functions.isAdmin(message) or message.author == message.server.owner:
				await functions.createMessage(client, message, key)
		if util.CommandPreTest(message,'createbind',key):
			if functions.isAdmin(message) or message.author == message.server.owner:
				roles = message.role_mentions
				if len(roles) > 0:
					msg = message.content[len(key+'createbind'):].strip()
					msg = msg.split(" ")
					functions.db.addBind(msg[0],msg[1],message.server.id)
		if util.CommandPreTest(message,'removebind',key):
			if functions.isAdmin(message) or message.author == message.server.owner:
				msg = message.content[len(key+'removebind'):].strip().split(" ")
				try:
					functions.db.removeBind(msg[1],message.server.id)
				except:
					pass
#############################################NSFW##################################################
		if util.CommandPreTest(message,'rule34',key):
			if functions.isnsfw(message):
				tags = message.content[len(key+'rule34'):].strip()
				tags = tags.replace(' ', '+')
				url = "https://rule34.xxx/index.php?page=dapi&s=post&q=index&limit=100&tags="+tags
				req = util.APIOpen(url)
				parse = ET.parse(req)
				list = [el.attrib.get('file_url') for el in parse.findall('.//post')]
				link = random.choice(list)
				await client.send_message(message.channel, link)
		if util.CommandPreTest(message,'real',key):
			if functions.isnsfw(message):
				tags = message.content[len(key+'real'):].strip()
				tags = tags.replace(' ', '+')
				url = "https://realbooru.com/index.php?page=dapi&s=post&q=index&limit=100&tags="+tags
				req = util.APIOpen(url)
				parse = ET.parse(req)
				list = [el.attrib.get('file_url') for el in parse.findall('.//post')]
				link = random.choice(list)
				await client.send_message(message.channel, link)
############################################VOICE##################################################
	for i in voiceplayers:
		if i.server == message.server.id:
			if util.CommandPreTest(message,'queue',key):
				url = message.content[len(key+'queue'):].strip()
				match = re.search(r'(https\:\/\/www\.youtube\.com\/watch\?v\=\S+)',url,re.M|re.I)
				if match:
					i.addToPlaylist(url)
			if util.CommandPreTest(message,'play',key):
				url = message.content[len(key+'play'):].strip()
				match = re.search(r'(https\:\/\/www\.youtube\.com\/watch\?v\=\S+)',url,re.M|re.I)
				if match:
					i.addToPlaylist(url)
				await i.join(message,client)
				await i.player(client,message)
			if util.CommandPreTest(message,'plist',key):
				url = message.content[len(key+'plist'):].strip()
				i.addPlaylist(url)
				print(i.getPlaylist())
			if ("sounds/"+message.content+".mp3" in sounds)or("sounds/"+message.content+".ogx" in sounds):
					for s in sounds:
						sv = re.search(r'(.*).(mp3|ogx)',s)
						if sv.group():
							if message.content in sv.group(1):
								await i.join(message,client)
								await i.playVoice(s)
								await i.disconnect()
			if util.CommandPreTest(message,'leave',key):
				try:
					await i.join(message,client)
					await i.disconnect()
				except:
					pass
############################################UPDATE DATABASE AND LISTS###############################
	if util.CommandPreTest(message, 'gods', "!"):
		await client.send_file(message.channel,'imgs/gods.jpg')
	if util.CommandPreTest(message,'howrude',"!"):
		await client.send_message(message.channel,'https://cdn.discordapp.com/attachments/155700698955251712/333277468435808256/HOW-RUDE.png')