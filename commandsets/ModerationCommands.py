import asyncio
import discord

from models.EmbedTemplate import EmbedTemplate
from models.Commands import Commands
from models.Command import Command

import re
class ModerationCommands(Commands):
    def __init__(self, moduleName, description, commandKey):
        commandList = self.fetchCommands(commandKey)
        super().__init__(moduleName, commandList, description, commandKey)
    def fetchCommands(self, commandKey):
        commandList = {}
        commandList["purge"] = Purge(commandKey)
        return commandList
    async def parse(self, message, server):
        if message.author.guild_permissions.administrator:
            await super().parse(message, server)
class Purge(Command):
    def __init__(self, commandKey):
        super().__init__(commandKey, "purge", """Purge channel of X amount of messages""", "{} {} {}".format(commandKey, "purge", "*<1-99>*"), ["empty"])
    async def run(self, message, server):
        pattern = re.escape(self.commandKey)+"\s("+"|".join(self.aliases)+")\s(\d+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                await message.delete()
                await message.channel.purge(limit=int(reg.group(2)))
        