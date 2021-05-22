import asyncio
import discord
from models.Commands import Commands
from models.Command import Command
from models.EmbedTemplate import EmbedTemplate
from forever.Steam import Steam_API
import re

class SteamCommands(Commands):
    def __init__(self, module_name, description, command_key, client, database, steam_api):
        self.client = client
        self.database = database
        self.steam_api = steam_api

        command_list = self.fetchCommands(command_key)
        super().__init__(module_name, command_list, description, command_key)
    def fetchCommands(self, command_key):
        command_list = {}
        command_list["test"] = Test(command_key, self.database, self.steam_api)

        return command_list
    async def parse(self, message, server):
        if message.author.id == 132166600513159168:
            print("ok")
            await super().parse(message, server)

class Test(Command):
    def __init__(self, command_key, database, steam_api):
        self.database = database
        self.steam_api = steam_api
        super().__init__(command_key, "test", """Testing""", "{} {}".format(command_key, "test"), [])
    async def run(self, message, server):
        pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")"
        reg = re.match(pattern, message.content)
        if reg:

            account, new_matches = await self.steam_api.get_complete_account(self.steam_api.steam_32bit_id_to_64bit(75851470))
            await message.channel.send(str(account))
            for i in new_matches:
                await self.database.create_dota_match(i)

            print(account.win_rate())
            print(account.match_history.wins)
            print(account.match_history.losses)
            print(account.match_history.total_matches)

