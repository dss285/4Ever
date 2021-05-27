import asyncio
import discord
from models.Commands import Commands
from models.Command import Command
from models.EmbedTemplate import EmbedTemplate
import subprocess
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
        command_list["shell"] = ShellCommand(command_key, self.client)
        return command_list
    async def parse(self, message, server):
        if message.author.id == 132166600513159168:
            await super().parse(message, server)
class ShellCommand(Command):
    def __init__(self, command_key, client):
        self.client = client
        super().__init__(command_key, "shell", """Shell""", "{} {} {}".format(command_key, "shell", "*shell command"), ['bash', 'sh'])
    async def run(self, message, server):
        pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")\s(.+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                splitted = reg.group(2).split(" ")
                output = subprocess.run(splitted, stdout=subprocess.PIPE, text=True, universal_newlines=True)
                if output.returncode == 0:
                    if len(output.stdout) < 1975:
                        await message.reply("""```{}```""".format(output.stdout))
                    else:
                        fo = open("tmp.txt", "w+")
                        fo.write(output.stdout)
                        fo.close()
                        await message.reply(file=discord.File("tmp.txt"))
                else:
                    await message.reply("Error from shell command: {}".format(output.stderr))
class EvalCommand(Command):
    def __init__(self, command_key, client):
        self.client = client
        super().__init__(command_key, "eval", """Eval""", "{} {} {}".format(command_key, "eval", "*evaled statement*"), ['ev'])
    async def run(self, message, server):
        pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")\s(.+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                output = str(eval(reg.group(2)))
                if len(output) < 1975:
                    await message.reply("""```{}```""".format(output))
                else:
                    fo = open("tmp.txt", "w+")
                    fo.write(output)
                    fo.close()
                    await message.reply(file=discord.File("tmp.txt"))


