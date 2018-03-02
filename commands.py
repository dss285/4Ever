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
from classes import utilities,image,database,main

from PIL import ImageFilter
from PIL import ImageFile
from PIL import Image

sounds = glob.glob('sounds/*')


ImageFile.LOAD_TRUNCATED_IMAGES = True
global voice
voice = None
async def commandRead(message, client, key, functions, conn, voiceplayers, util=utilities.Utilities()):
	if util.CommandPreTest(message,'help',key):
		helpdesc =""":question:** Help**
		
			:gear:** Commands**
			!help - This panel
			!google keywords - Google search
			
			:frame_photo:** Image Manipulation**
			!resize width height url - Resizes image to wanted sizes
			!blendimg url url2 - Needs 2 same size and same color mode images to blend them together
			

			:musical_note:** Voice Related**
			!play (URL) - Plays youtube URL
			
			
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

#################################################IMAGE RELATED#######################################
	if util.CommandPreTest(message,'resize',key):
		name = message.content[len(key+'resize'):].strip()
		name = name.split(' ')
		width = int(name[0])
		height = int(name[1])
		size = (width,height)
		url = name[2]
		img = functions.openImgUrl(url)
		img = img.resize(size, Image.ANTIALIAS);
		img.save('temp.png','PNG')
		await client.send_file(message.channel, 'temp.png')
	if message.content.startswith(key+'blur'):
		name = message.content[len(key+'blur'):].strip()
		name = name.split(" ")
		url = name[1]
		bluramount = int(name[0])
		img = functions.openImgUrl(url)
		img = img.filter(ImageFilter.GaussianBlur(bluramount));
		img.save('temp.png','PNG')
		await client.send_file(message.channel, 'temp.png')
#############################################ADMIN FUNCTIONS##################################################		
	if util.CommandPreTest(message,'adminRole',key):
		server_owner = message.author.server.owner.id
		server = message.server.id
		print(server)
		if server_owner == message.author.id:
			msg = message.content[len(key+'adminRole <@&'):].strip()
			msg = msg.replace('>','')
			msg = int(msg)
			if not msg in functions.adminRole:
				sql_d = "DELETE FROM server WHERE serverid=%s"
				args_d = (int(server),)
				conn.delete(sql_d,args_d)
				sql = "INSERT INTO server (admin_role, serverid) VALUES (%s, %s)"
				args = (int(msg),int(server))
				conn.insert(sql,args)
				conn.updateDics("server")
	if util.CommandPreTest(message,'empty',key):
		for i in functions.adminRole:
			for r in message.author.roles:
				if str(i[0]) in r.id:
					amountsOfDel = message.content[len(key+'empty'):].strip()
					amountsOfDel = int(amountsOfDel)
					print(amountsOfDel)
					deleted = await client.purge_from(message.channel, limit=amountsOfDel+1)
					break;
	if util.CommandPreTest(message,'nsfw',key):
		functions.nsfwchannel(message, client,key)
#############################################NSFW##################################################
	if util.CommandPreTest(message,'rule34',key):
		for i in functions.nsfwchannels:
			var = i
			if int(message.channel.id) in var:
				tags = message.content[len(key+'rule34'):].strip()
				tags = tags.replace(' ', '+')
				url = "https://rule34.xxx/index.php?page=dapi&s=post&q=index&limit=100&tags="+tags
				req = urllib.request.urlopen(url)
				parse = ET.parse(req)
				list = [el.attrib.get('file_url') for el in parse.findall('.//post')]
				link = random.choice(list)
				print(link)

				await client.send_message(message.channel, link)
	if util.CommandPreTest(message,'real',key):
		for i in functions.nsfwchannels:
			var = i
			if int(message.channel.id) in var:
				tags = message.content[len(key+'real'):].strip()
				tags = tags.replace(' ', '+')
				url = "https://realbooru.com/index.php?page=dapi&s=post&q=index&limit=100&tags="+tags
				req = urllib.request.urlopen(url)
				parse = ET.parse(req)
				list = [el.attrib.get('file_url') for el in parse.findall('.//post')]
				link = random.choice(list)
				await client.send_message(message.channel, link)
#############################################VOICE##################################################
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
								await client.delete_message(message)
								await i.disconnect()
			if util.CommandPreTest(message,'leave',key):
				await i.join(message,client)
				await i.disconnect()
		#if util.CommandPreTest(message,'join',key):
			# for i in adminRole:
				# for r in message.author.roles:
					# if str(i[0]) in r.id:
						# try:
							# voice = await functions.join(message,client)
						# except:
							# client.send_message(message.channel,"Already in voice channel!")
############################################UPDATE DATABASE AND LISTS###############################
	if util.CommandPreTest(message,'arrays',key):
		await client.send_message(message.channel, "Updating arrays")
		ser = functions.db.updateDics("server")
		nsfw = functions.db.updateDics("nsfw")
		functions.insert(nsfw,ser)
		print(nsfwchannels)
		print(adminRole)
#####################################################MISCELLANEOUS##################################
	if util.CommandPreTest(message,'google',key):
		name = message.content[len(key+'google'):].strip()
		name = name.replace(" ", "+")
		await client.send_message(message.channel, 'https://www.google.fi/?gws_rd=ssl#q={}'.format(name))
	if util.CommandPreTest(message,'gta businesses',key):
		await client.send_file(message.channel,'imgs/bikersbusinesses.png')
	if util.CommandPreTest(message,'how rude',key):
		await client.send_message(message.channel,'https://cdn.discordapp.com/attachments/155700698955251712/333277468435808256/HOW-RUDE.png')
####################################################VOICE EFFECTS ##################################

