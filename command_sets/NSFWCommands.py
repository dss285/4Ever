import asyncio
import discord
import time
import re

from forever import NSFW
from models.EmbedTemplate import EmbedTemplate
from models.Commands import Commands, Command

class NSFWCommands(Commands):
    def __init__(self, module_name, description, command_key):
        command_list = self.fetchCommands(command_key)
        self.rate_limit = 5
        self.count = 0
        self.timer = {"start": time.time(), "end": time.time()+5}
        super().__init__(module_name, command_list, description, command_key)
    def fetchCommands(self, command_key):
        command_list = {}
        command_list["rule34"] = Rule34(command_key)
        command_list["realbooru"] = Realbooru(command_key)
        command_list["safebooru"] = Safebooru(command_key)
        command_list["gelbooru"] = Gelbooru(command_key)
        command_list["danbooru"] = Danbooru(command_key)
        return command_list
    async def parse(self, message, server):
        if self.timer["start"] < time.time() < self.timer["end"]:
            self.count += 1
        else:
            self.timer["start"] = time.time()
            self.timer["end"] = time.time()+5
            self.count = 0
        if self.count < self.rate_limit:
            await super().parse(message, server)
            self.count += 1
        else:
            em = EmbedTemplate(title="Rate Limit", description="You're being rate limited. Try again soon")
            await message.channel.send(embed=em)
class Rule34(Command):
    def __init__(self, command_key):
        super().__init__(command_key, "rule34", """Rule34 Search""", "{} {} {}".format(command_key, "rule34", "*<tags>*"), ["r34"])
    async def run(self, message, server):
        pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")\s(.+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                em = await NSFW.rule34XXX(reg.group(2))
                await message.channel.send(embed=em)    
class Realbooru(Command):
    def __init__(self, command_key):
        super().__init__(command_key, "realbooru", """Realbooru Search""", "{} {} {}".format(command_key, "realbooru", "*<tags>*"), ["real"])
    async def run(self, message, server):
        pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")\s(.+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                em = await NSFW.realbooru(reg.group(2))
                await message.reply(embed=em)
class Safebooru(Command):
    def __init__(self, command_key):
        super().__init__(command_key, "safebooru", """Safebooru Search""", "{} {} {}".format(command_key, "safebooru", "*<tags>*"), ["safe"])
    async def run(self, message, server):
        pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")\s(.+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                em = await NSFW.safebooru(reg.group(2))
                await message.reply(embed=em)
class Gelbooru(Command):
    def __init__(self, command_key):
        super().__init__(command_key, "gelbooru", """Gelbooru Search""", "{} {} {}".format(command_key, "gelbooru", "*<tags>*"), ["gel"])
    async def run(self, message, server):
        pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")\s(.+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                em = await NSFW.gelbooru(reg.group(2))
                await message.reply(embed=em)
class Danbooru(Command):
    def __init__(self, command_key):
        super().__init__(command_key, "danbooru", """Danbooru Search""", "{} {} {}".format(command_key, "danbooru", "*<tags>*"), ["dan"])
    async def run(self, message, server):
        pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")\s(.+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                em = await NSFW.danbooru(reg.group(2))
                await message.reply(embed=em)
