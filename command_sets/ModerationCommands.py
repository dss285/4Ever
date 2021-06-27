import asyncio
import discord

from models.EmbedTemplate import EmbedTemplate
from models.Commands import Commands, Command
from forever.Utilities import Args

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
        self.args = Args(limit=Args.INT_ARG)
        self.args.set_pattern(command_key, self.aliases)
    async def run(self, message, server):
        parse = self.parse(message.content)
        if parse:
            await message.delete()
            await message.channel.purge(limit=int(parse["limit"]))
        