import asyncio
import discord
from models.EmbedTemplate import EmbedTemplate
from models.Commands import Commands, Command
from forever.Voice import VoicePlayer
from forever.Utilities import Args
import re
class VoiceCommands(Commands):
    def __init__(self, module_name, description, command_key, client):
        self.client = client
        command_list = self.fetch_commands(command_key)
        super().__init__(module_name, command_list, description, command_key)

    def fetch_commands(self, command_key):
        command_list = {}
        command_list["resume"] = Resume(command_key)
        command_list["play"] = Play(command_key, self.client)
        command_list["pause"] = Pause(command_key)
        command_list["skip"] = Skip(command_key)
        command_list["leave"] = Leave(command_key, self.client)
        command_list["sound"] = Sound(command_key, self.client)
        return command_list

class Play(Command):
    YOUTUBE_REGEX = "(?P<{}>http[s]?:\/\/(www\.)?(youtube\.com|youtu\.be)\/(watch\?.*v=)?.*)"
    def __init__(self, command_key, client):
        self.client = client
        super().__init__(command_key, "play", """Play music, by giving URLs""", f"{command_key} play *<url>*", ["test"])
        self.args = Args(url=Play.YOUTUBE_REGEX)
        self.args.set_pattern(command_key, self.aliases)
    async def run(self, message, server):
        parse = self.args.parse(message.content)
        if parse:
            if message.author.voice.channel:
                if server:
                    if not server.voice:
                        vc = await message.author.voice.channel.connect()
                        server.voice = VoicePlayer(vc, message.channel, self.client)
                    if server.voice.vc.is_connected():
                        if parse.get("url"):
                            await server.voice.handle(parse.get("url"))
                    else:
                        server.voice = None
                        await self.run(message, server)
class Resume(Command):
    def __init__(self, command_key):
        super().__init__(command_key, "resume", """Resume paused track""", f"{command_key} resume", [])
    async def run(self, message, server):
        if server:
            if server.voice:
                await server.voice.resume()
class Pause(Command):
    def __init__(self, command_key):
        super().__init__(command_key, "pause", """Pause currently playing track""", f"{command_key} pause", [])
    async def run(self, message, server):
        if server:
            if server.voice:
                await server.voice.pause()
class Skip(Command):
    def __init__(self, command_key):
        super().__init__(command_key, "skip", """Skip currently playing track""", f"{command_key} skip", [])
    async def run(self, message, server):
        if server:
            if server.voice:
                await server.voice.skip()
class Leave(Command):
    def __init__(self, command_key, client):
        self.client = client
        super().__init__(command_key, "leave", """Leaves the channel""", f"{command_key} leave", [])
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
    def __init__(self, command_key, client):
        self.client = client
        super().__init__(command_key, "sound", """Plays a certain sound""", f"{command_key} sound <*list*|*sound name*>", [])
        self.args = Args(sound=Args.ANY_ARG)
        self.args.set_pattern(command_key, self.aliases)
    async def run(self, message, server):
        parse = self.args.parse(message.content)
        if parse:
            if message.author.voice.channel:
                if server:
                    if not server.voice:
                        vc = await message.author.voice.channel.connect()
                        server.voice = VoicePlayer(vc, message.channel, self.client)
                    if server.voice.vc.is_connected():
                        if parse.get("sound") == "list":
                            em = EmbedTemplate(title="Sounds", description="\n".join(sorted(server.voice.sounds.keys())))
                            await message.channel.send(embed=em)
                        elif parse.get("sound") in server.voice.sounds.keys():
                            await server.voice.playFile(server.voice.sounds[parse.get("sound")])
                    else:
                        server.voice = None
                        await self.run(message, server)

