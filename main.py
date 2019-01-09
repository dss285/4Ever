#!/usr/bin/python
import discord
import asyncio
import commands
import config
import time
import json
import glob
from random import randint
from classes import utilities,image,database,main,voicePlayer,warframe
client = discord.Client()
voiceplayers = []
msg = ""
alertList = {}
msgs = ""
functions = main.Main(config.host,config.username,config.password,config.databasename)
@client.event
async def on_ready():
	dicts = functions.db.dicts
	functions.dicts = dicts
	await client.change_presence(game=discord.Game(name='!e help for help'))
	print(discord.__version__)
	for i in client.servers:
		voiceplayers.append(voicePlayer.voicePlayer(i.id))

		
	
@client.event
async def on_message(message):
	if message.author.id!="211176330128130048":
		await commands.commandRead(message, client,'!e ',functions ,functions.db, voiceplayers)
async def loopR(client, functions):
	await client.wait_until_ready()
	while not client.is_closed:
		voiceplayers = []
		sounds = glob.glob('sounds/*')
		functions.db.updateDict()
		functions.dicts = functions.db.dicts
		await warframe.warframe().loop(client, msg,functions.db)
		tmp = []
		for i in client.servers:
			tmp.append(i.id)
			if not functions.isServerIn(i.id):
				sql = "INSERT INTO server VALUES (%s,%s)"
				args = ("asd",i.id)
				functions.db.insert(sql,args)
				
		for i in functions.dicts.keys():
			if i not in tmp:
				sql = "DELETE FROM server WHERE serverid=%s"
				args = (i,)
				functions.db.delete(sql,args)
		chn = client.get_channel("521410204915466277")
		msgs = "```"+json.dumps(functions.dicts, sort_keys=True, indent=4)+"```"
		try:
			temp = await client.send_message(chn,msgs)
			await asyncio.sleep(29)
			await client.delete_message(temp)
		except:
			pass
		await asyncio.sleep(1)
client.loop.create_task(loopR(client, functions))
client.run(config.bot_token)

