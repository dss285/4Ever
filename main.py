#!/usr/bin/python
import discord
import asyncio
import commands
import config
from classes import utilities,image,database,main,voicePlayer
client = discord.Client()
voiceplayers = []
functions = main.Main(config.host,config.username,config.password,config.databasename)


@client.event
async def on_ready():
	servers = functions.db.updateDics("server")
	functions.insertInto(servers)
	await client.change_presence(game=discord.Game(name='!help for help'))
	print(discord.__version__)
	print(servers)
	for i in client.servers:
		print(i.name)
		voiceplayers.append(voicePlayer.voicePlayer(i.id))
	else:
		print(voiceplayers)
	
@client.event
async def on_message(message):
	await commands.commandRead(message, client,'!',functions ,functions.db, voiceplayers)
client.run(config.bot_token)

