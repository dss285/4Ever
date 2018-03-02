#!/usr/bin/python
import discord
import asyncio
import commands
from classes import utilities,image,database,main,voicePlayer
client = discord.Client()
voiceplayers = []
host = ""
username = ""
password = ""
databasename = ""
functions = main.Main(host,username,password,databasename)


@client.event
async def on_ready():
	nsfwchannels = functions.db.updateDics("nsfw")
	servers = functions.db.updateDics("server")
	functions.insertInto(nsfwchannels,servers)
	await client.change_presence(game=discord.Game(name='!help for help'))
	print(discord.__version__)
	print(nsfwchannels)
	print(servers)
	for i in client.servers:
		print(i.name)
		voiceplayers.append(voicePlayer.voicePlayer(i.id))
	else:
		print(voiceplayers)
	
@client.event
async def on_message(message):
	await commands.commandRead(message, client,'!',functions ,functions.db, voiceplayers)
client.run('BOT TOKEN')

