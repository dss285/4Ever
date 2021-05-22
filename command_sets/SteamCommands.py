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
        command_list["dotaprofile"] = DotaProfile(command_key, self.database, self.steam_api)

        return command_list
    # async def parse(self, message, server):
    #     if message.author.id == 132166600513159168:
    #         await super().parse(message, server)

class DotaProfile(Command):
    def __init__(self, command_key, database, steam_api):
        self.database = database
        self.steam_api = steam_api
        super().__init__(command_key, "dotaprofile", """Testing""", "{} {}".format(command_key, "dotaprofile"), [])
    async def run(self, message, server):
        pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")"+"\s(?:(\d+)|(?:https:\/\/steamcommunity\.com\/(?:profiles\/(\d+)|id\/(.+))))"
        reg = re.match(pattern, message.content)
        if reg:
            steam_32id = None
            steam_64id = None

            vanity_url = reg.group(4)
           
            steam_profile_id = reg.group(3)
            steam_id = reg.group(2)
            if vanity_url is not None:
                if vanity_url[len(vanity_url)-1] == '/':
                    vanity_url = vanity_url[:len(vanity_url)-1]
                steam_64id = await self.steam_api.resolve_vanity_url(vanity_url)
                steam_32id = self.steam_api.steam_64bit_id_to_32bit(steam_64id)
            elif steam_profile_id is not None:
                steam_32id = self.steam_api.steam_64bit_id_to_32bit(steam_profile_id)
                steam_64id = int(steam_profile_id)
            elif steam_id is not None:
                steam_32id = int(steam_id) if steam_id < 76561197960265728 else self.steam_api.steam_32bit_id_to_64bit(steam_id)
                steam_64id = int(steam_id) if steam_id > 76561197960265728 else self.steam_api.steam_64bit_id_to_32bit(steam_id)
            await message.reply("> Might take a while, sit tight")
            account, new_matches = await self.steam_api.get_complete_account(steam_64id)
            for i in new_matches:
                await self.database.create_dota_match(i)

            em = EmbedTemplate(title=account.steam_profile.name,
            description="Win rate: {}%\nWins: {}\nLosses: {}\nTotal matches:{}".format(
                account.win_rate()*100,
                account.match_history.wins,
                account.match_history.losses,
                account.match_history.total_matches
            ))
            em.set_thumbnail(url=account.steam_profile.get_full_avatar())
            await message.reply(embed=em)
class DotaHeroProfile():
    def __init__(self, command_key, database, steam_api):
        self.database = database
        self.steam_api = steam_api
        super().__init__(command_key, "dotaheroprofile", """Testing""", "{} {}".format(command_key, "dotaheroprofile"), [])
    async def run(self, message, server):
        pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")"+"\s(\S+)\s(?:(\d+)|(?:https:\/\/steamcommunity\.com\/(?:profiles\/(\d+)|id\/(.+))))"
        reg = re.match(pattern, message.content)
        if reg:
            steam_32id = None
            steam_64id = None
class Test(Command):
    def __init__(self, command_key, database, steam_api):
        self.database = database
        self.steam_api = steam_api
        super().__init__(command_key, "test", """Testing""", "{} {}".format(command_key, "test"), [])
    async def run(self, message, server):
        pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")"
        reg = re.match(pattern, message.content)
        if reg:

            account, new_matches = await self.steam_api.get_complete_account(self.steam_api.steam_32bit_id_to_64bit(85485710))
            await message.channel.send(str(account))
            for i in new_matches:
                await self.database.create_dota_match(i)
            msg_string = "Steam name: {}\nWin rate: {}\nWins: {}\nLosses: {}\nTotal matches:{}".format(
                account.steam_profile.name,
                account.win_rate(),
                account.match_history.wins,
                account.match_history.losses,
                account.match_history.total_matches
            )
            account, new_matches = await self.steam_api.get_complete_account(self.steam_api.steam_32bit_id_to_64bit(75851470))
            await message.channel.send(str(account))
            for i in new_matches:
                await self.database.create_dota_match(i)
            msg_string += "Steam name: {}\nWin rate: {}\nWins: {}\nLosses: {}\nTotal matches:{}".format(
                account.steam_profile.name,
                account.win_rate(),
                account.match_history.wins,
                account.match_history.losses,
                account.match_history.total_matches
            )

            await message.channel.send(msg_string)


