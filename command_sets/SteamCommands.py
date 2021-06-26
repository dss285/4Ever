import asyncio
import discord
from models.EmbedTemplate import EmbedTemplate
from models.Commands import Commands, Command
from forever.Steam import Steam_API
from forever.Utilities import Args
import re

class SteamCommands(Commands):
    STEAM_URL_REGEX = "(?:(?P<{}>\d+)|(?:https:\/\/steamcommunity\.com\/(?:profiles\/(?P<steamid>\d+)|id\/(?P<profile>.+))))"
    def __init__(self, module_name, description, command_key, client, database, steam_api):
        self.client = client
        self.database = database
        self.steam_api = steam_api

        command_list = self.fetch_commands(command_key)
        super().__init__(module_name, command_list, description, command_key)
    def fetch_commands(self, command_key):
        command_list = {}
        #command_list["test"] = Test(command_key, self.database, self.steam_api)
        command_list["dotaprofile"] = DotaProfile(command_key, self.database, self.steam_api)
        command_list["dotaheroprofile"] = DotaHeroProfile(command_key, self.database, self.steam_api)

        return command_list
    # async def parse(self, message, server):
    #     if message.author.id == 132166600513159168:
    #         await super().parse(message, server)

class DotaProfile(Command):
    def __init__(self, command_key, database, steam_api):
        self.database = database
        self.steam_api = steam_api
        super().__init__(command_key, "dotaprofile", """Testing""", f"{command_key} dotaprofile", [])
        self.args = Args(steamarg=SteamCommands.STEAM_URL_REGEX)
        self.args.set_pattern(command_key, self.aliases)
    async def run(self, message, server):
        parse = self.args.parse(message.content)
        if parse:
            steam_32id = None
            steam_64id = None

            vanity_url = parse.get("profile")
           
            steam_profile_id = parse.get("steamid")
            steam_id = parse.get('steamarg')
            if vanity_url is not None:
                if vanity_url[len(vanity_url)-1] == '/':
                    vanity_url = vanity_url[:len(vanity_url)-1]
                steam_64id = await self.steam_api.resolve_vanity_url(vanity_url)
                if steam_64id:
                    steam_32id = self.steam_api.steam_64bit_id_to_32bit(steam_64id)
            elif steam_profile_id is not None:
                steam_32id = self.steam_api.steam_64bit_id_to_32bit(steam_profile_id)
                steam_64id = int(steam_profile_id)
            elif steam_id is not None:
                steam_32id = int(steam_id) if steam_id < 76561197960265728 else self.steam_api.steam_32bit_id_to_64bit(steam_id)
                steam_64id = int(steam_id) if steam_id > 76561197960265728 else self.steam_api.steam_64bit_id_to_32bit(steam_id)
            if steam_64id:
                await message.reply("> Might take a while, sit tight")
                account, new_matches = await self.steam_api.get_complete_account(steam_64id)
                for i in new_matches:
                    await self.database.create_dota_match(i)

            em = EmbedTemplate(title=account.steam_profile.name,
            description=f"Win rate: {account.win_rate()*100}%\nWins: {account.match_history.wins}\nLosses: {account.match_history.losses}\nTotal matches:{account.match_history.total_matches}")
            em.set_thumbnail(url=account.steam_profile.get_full_avatar())
            await message.reply(embed=em)
class DotaHeroProfile(Command):
    def __init__(self, command_key, database, steam_api):
        self.database = database
        self.steam_api = steam_api
        super().__init__(command_key, "dotaheroprofile", """Testing""", f"{command_key} dotaheroprofile", [])
        self.args = Args(steamarg=SteamCommands.STEAM_URL_REGEX, hero=Args.ANY_ARG)
        self.args.set_pattern(command_key, self.aliases)
    async def run(self, message, server):
        parse = self.args.parse(message.content)
        if parse:
            steam_32id = None
            steam_64id = None
            hero_name = parse.get("hero")
            hero_id = self.database.runtime["dota"]["heroes"]["name"].get(hero_name)

            if hero_id:
                vanity_url = parse.get("profile")
                steam_profile_id = parse.get("steamid")
                steam_id = parse.get("steamarg")
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
                account, new_matches = await self.steam_api.get_complete_account(steam_64id, hero_id, True)
                for i in new_matches:
                    await self.database.create_dota_match(i)
                em = EmbedTemplate(title=account.steam_profile.name,
                description=f"Win rate: {account.win_rate()*100}%\nWins: {account.match_history.wins}\nLosses: {account.match_history.losses}\nTotal matches:{account.match_history.total_matches}")
                em.set_thumbnail(url=account.steam_profile.get_full_avatar())
                await message.reply(embed=em)
# class Test(Command):
#     def __init__(self, command_key, database, steam_api):
#         self.database = database
#         self.steam_api = steam_api
#         super().__init__(command_key, "test", """Testing""", f"{command_key} test", [])
#     async def run(self, message, server):
#         pattern = re.escape(self.prefix)+"\s("+"|".join(self.aliases)+")"
#         reg = re.match(pattern, message.content)
#         if reg:

#             account, new_matches = await self.steam_api.get_complete_account(self.steam_api.steam_32bit_id_to_64bit(85485710))
#             await message.channel.send(str(account))
#             for i in new_matches:
#                 await self.database.create_dota_match(i)
#             msg_string = "Steam name: {}\nWin rate: {}\nWins: {}\nLosses: {}\nTotal matches:{}".format(
#                 account.steam_profile.name,
#                 account.win_rate(),
#                 account.match_history.wins,
#                 account.match_history.losses,
#                 account.match_history.total_matches
#             )
#             account, new_matches = await self.steam_api.get_complete_account(self.steam_api.steam_32bit_id_to_64bit(75851470))
#             await message.channel.send(str(account))
#             for i in new_matches:
#                 await self.database.create_dota_match(i)
#             msg_string += "Steam name: {}\nWin rate: {}\nWins: {}\nLosses: {}\nTotal matches:{}".format(
#                 account.steam_profile.name,
#                 account.win_rate(),
#                 account.match_history.wins,
#                 account.match_history.losses,
#                 account.match_history.total_matches
#             )

#             await message.channel.send(msg_string)


