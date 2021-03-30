import asyncio
import discord
from models.Commands import Commands
from models.Command import Command
from models.EmbedTemplate import EmbedTemplate
import re

class BotAdminCommands(Commands):
    def __init__(self, module_name, description, command_key, client, database):
        self.client = client
        self.database = database
        command_list = self.fetchCommands(command_key)
        super().__init__(module_name, command_list, description, command_key)

    def fetchCommands(self, command_key):
        command_list = {}
        command_list["eval"] = EvalCommand(command_key, self.client)
        return command_list
    async def parse(self, message, server):
        if message.author.id == 132166600513159168:
            await super().parse(message, server)
class EvalCommand(Command):
    def __init__(self, command_key, client):
        self.client = client
        super().__init__(command_key, "eval", """Eval""", "{} {} {}".format(command_key, "eval", "*evaled statement*"), ['ev'])
    async def run(self, message, server):
        pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")\s(.+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                await message.reply(str(eval(reg.group(2))))

