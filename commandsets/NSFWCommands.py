import asyncio
import discord
from forever.NSFW import NSFW
from models.Commands import Commands
from models.Command import Command
from models.EmbedTemplate import EmbedTemplate
import re

class NSFWCommands(Commands):
    def __init__(self, moduleName, description, commandKey):
        commandlist = self.fetchCommands(commandKey)
        super().__init__(moduleName, commandlist, description, commandKey)
    def fetchCommands(self, commandKey):
        commandlist = {}
        commandlist["rule34"] = Rule34(commandKey)
        commandlist["realbooru"] = Realbooru(commandKey)
        return commandlist
class Rule34(Command):
    def __init__(self, commandKey):
        super().__init__(commandKey, "rule34", """Rule34 Search""", "{} {} {}".format(commandKey, "rule34", "*<tags>*"), ["r34"])
    async def run(self, message, server):
        pattern = re.escape(self.commandKey)+"\s("+"|".join(self.aliases)+")\s(.+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                data = await NSFW.rule34XXX(reg.group(2))
                em = EmbedTemplate(title=reg.group(2).title(), description = data["tags"].replace("*",""))
                em.set_image(url=data["img"])
                await message.channel.send(embed=em)
class Realbooru(Command):
    def __init__(self, commandKey):
        super().__init__(commandKey, "realbooru", """Realbooru Search""", "{} {} {}".format(commandKey, "realbooru", "*<tags>*"), ["real"])
    async def run(self, message, server):
        pattern = re.escape(self.commandKey)+"\s("+"|".join(self.aliases)+")\s(.+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                data = await NSFW.realbooru(reg.group(2))
                em = EmbedTemplate(title=reg.group(2).title(), description = data["tags"].replace("*",""))
                em.set_image(url=data["img"])
                await message.reply(embed=em)
