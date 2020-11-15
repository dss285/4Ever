import asyncio
import discord
from abstract.Commands import Commands
from abstract.Command import Command
from abstract.EmbedTemplate import EmbedTemplate
from voice.VoicePlayer import VoicePlayer
import re
class VoiceCommands(Commands):
    def __init__(self, moduleName, description, commandKey, client):
        self.client = client
        commandlist = self.fetchCommands(commandKey)
        super().__init__(moduleName, commandlist, description, commandKey)

    def fetchCommands(self, commandKey):
        commandlist = {}
        commandlist["resume"] = Resume(commandKey)
        commandlist["play"] = Play(commandKey, self.client)
        commandlist["pause"] = Pause(commandKey)
        commandlist["skip"] = Skip(commandKey)
        commandlist["leave"] = Leave(commandKey, self.client)
        commandlist["sound"] = Sound(commandKey, self.client)
        return commandlist

class Play(Command):
    def __init__(self, commandKey, client):
        self.client = client
        super().__init__(commandKey, "play", """Play music, by giving URLs""", "{} {} {}".format(commandKey, "play", "*<url>*"), ["test"])

        
    async def run(self, message, server):
        pattern = re.escape(self.commandKey)+"\s("+"|".join(self.aliases)+")\s(http[s]?:\/\/(www\.)?(youtube\.com|youtu\.be)\/(watch\?.*v=)?.*)"
        reg = re.match(pattern, message.content)
        if reg:
            if message.author.voice.channel:
                if server:
                    if not server.voice:
                        vc = await message.author.voice.channel.connect()
                        server.voice = VoicePlayer(vc, message.channel, self.client)
                    if server.voice.vc.is_connected():
                        if reg.group(2):
                            await server.voice.handle(reg.group(2))
                    else:
                        server.voice = None
                        await self.run(message, server)
class Resume(Command):
    def __init__(self, commandKey):
        super().__init__(commandKey, "resume", """Resume paused track""", "{} {}".format(commandKey, "resume"), [])
    async def run(self, message, server):
        if server:
            if server.voice:
                await server.voice.resume()
class Pause(Command):
    def __init__(self, commandKey):
        super().__init__(commandKey, "pause", """Pause currently playing track""", "{} {}".format(commandKey, "pause"), [])
    async def run(self, message, server):
        if server:
            if server.voice:
                await server.voice.pause()
class Skip(Command):
    def __init__(self, commandKey):
        super().__init__(commandKey, "skip", """Skip currently playing track""", "{} {}".format(commandKey, "skip"), [])
    async def run(self, message, server):
        if server:
            if server.voice:
                await server.voice.skip()
class Leave(Command):
    def __init__(self, commandKey, client):
        self.client = client
        super().__init__(commandKey, "leave", """Leaves the channel""", "{} {}".format(commandKey, "leave"), [])
    async def run(self, message, server):
        vc = next((x for x in self.client.voice_clients if message.guild == x.guild), None)
        if vc.is_connected():
            em = EmbedTemplate(title="Left Voice Channel",description="Bot has left voice channel")
            await vc.disconnect()
            await message.channel.send(embed=em)
            if server:
                if server.voice:
                    server.voice = None
class Sound(Command):
    def __init__(self, commandKey, client):
        self.client = client
        super().__init__(commandKey, "sound", """Plays a certain sound""", "{} {} {}".format(commandKey, "sound", "<*list*|*sound name*>"), [])
    async def run(self, message, server):
        pattern = re.escape(self.commandKey)+"\s("+"|".join(self.aliases)+")\s([a-zA-Z0-9]+)"
        reg = re.match(pattern, message.content)
        if reg:
            if message.author.voice.channel:
                if server:
                    if not server.voice:
                        vc = await message.author.voice.channel.connect()
                        server.voice = VoicePlayer(vc, message.channel, self.client)
                    if server.voice.vc.is_connected():
                        if reg.group(2) == "list":
                            em = EmbedTemplate(title="Sounds", description="\n".join(sorted(server.voice.sounds.keys())))
                            await message.channel.send(embed=em)
                        elif reg.group(2) in server.voice.sounds.keys():
                            await server.voice.playFile(server.voice.sounds[reg.group(2)])
                    else:
                        server.voice = None
                        await self.run(message, server)

