import asyncio
import discord

from models.EmbedTemplate import EmbedTemplate
from models.Commands import Commands, Command

import re
class ModerationCommands(Commands):
    def __init__(self, module_name, description, command_key):
        command_list = self.fetch_commands(command_key)
        super().__init__(module_name, command_list, description, command_key)
    def fetch_commands(self, command_key):
        command_list = {}
        command_list["purge"] = Purge(command_key)
        return command_list
    async def parse(self, message, server):
        if message.author.guild_permissions.administrator:
            await super().parse(message, server)
class Purge(Command):
    def __init__(self, command_key):
        super().__init__(command_key, "purge", """Purge channel of X amount of messages""", f"{command_key} purge *<1-99>*", ["empty"])
    async def run(self, message, server):
        pattern = re.escape(self.prefix)+"\s("+"|".join(self.aliases)+")\s(\d+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                await message.delete()
                await message.channel.purge(limit=int(reg.group(2)))
        