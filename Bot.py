import aiohttp
import discord
import asyncio
from datetime import datetime
import time
import traceback
import config

import forever.Utilities
from models.EmbedTemplate import EmbedTemplate

from forever.Utilities import log
from forever.Database import DB_API
from forever.Newswire import Newswire
from forever.Warframe import DropTables, Worldstate
from forever.Steam import Steam_API
from forever.Arknights import  PenguinStats
from models.Server import Server

from command_sets.VoiceCommands import VoiceCommands
from command_sets.ModerationCommands import ModerationCommands
from command_sets.MathCommands import MathCommands
from command_sets.WarframeCommands import WarframeCommands
from command_sets.ForeverCommands import ForeverCommands
from command_sets.GFLCommands import GFLCommands
from command_sets.NSFWCommands import NSFWCommands
from command_sets.RoleCommands import RoleCommands
from command_sets.BotAdminCommands import BotAdminCommands
from command_sets.SteamCommands import SteamCommands

class Bot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aiosession = None
        self.database = DB_API(config.host, config.user, config.password, config.database, self)
        self.worldstate = Worldstate()
        self.warframe_droptables = DropTables()
        self.penguin_stats = PenguinStats(self.database)
        self.steam_api = Steam_API("http://api.steampowered.com", config.steam_api_key)
        self.newswire = Newswire()
        self.command_key = "\u0024"
        self.commands = {
            "botadmin" :    BotAdminCommands("Bot Admin", "", self.command_key+"botadmin", self, self.database),
            "voice" :       VoiceCommands("Voice", "This module has all the voice commands related to the bot", self.command_key+"voice", self),
            "moderation" :  ModerationCommands("Moderation", "This module has all the moderation commands related to the bot", self.command_key+"mod"),
            "role" :        RoleCommands("Role", "This module has all the role commands", self.command_key+"role", self, self.database),
            "math" :        MathCommands("Math", "This module has math commands", self.command_key+"math", self),
            "warframe" :    WarframeCommands("Warframe", "Warframe module", self.command_key+"wf", self, self.database, self.warframe_droptables),
            "gfl" :         GFLCommands("Girls' Frontline", "GFL Module", self.command_key+"gfl", self, self.database),
            "steam" :       SteamCommands("Steam", "Steam Module", self.command_key+"steam", self, self.database, self.steam_api),
            "forever" :     ForeverCommands("Forever", "Main module of the bot", self.command_key+"fe", self, self.database, self.newswire),
            "nsfw" :        NSFWCommands("NSFW", "NSFW Module", self.command_key+"nsfw")
        }
        self.server_sync_task = None
    async def basic_loop(self,):
        await self.wait_until_ready()
        await self.database.init_runtime()
        await self.penguin_stats.parse()
        self.server_sync_task = self.loop.create_task(self.server_sync())
        while True:
            try:
                await self.worldstate.get_data(self.database.runtime)

                await self.newswire.get_data()

                gtadata = {"gtanw" : self.newswire.nw_items.values()}
                data = {**gtadata, **self.worldstate.runtime}
                await asyncio.sleep(2)
                for i in self.database.runtime["servers"].values():
                    self.loop.create_task(i.updateMessages(data, self.database))
            except Exception as e:
                
                print("Error, logged")
                log([f"[BASE LOOP][{time.time()}] {e}", traceback.format_exc()+"\r\n"])

            await asyncio.sleep(120)
    async def server_sync(self,):
        await self.wait_until_ready()
        while not self.database.init_done:
            await asyncio.sleep(5)
        while True:
            guilds = set(self.guilds)
            for x in self.guilds:
                if x.id not in self.database.runtime["servers"]:
                    tmp = Server(x.id, x, None, {}, [], set(), {})
                    await self.database.create_server(x.id)
                    self.database.runtime["servers"][x.id] = tmp
            for i, j in self.database.runtime["servers"].items():
                if j.discord_server not in guilds:
                    await self.database.delete_server(i)
                if j.voice != None:
                    j.voice.update_sounds()
            await asyncio.sleep(15)
    async def on_ready(self,):
        self.aiosession = aiohttp.ClientSession()
        self.newswire.session = self.aiosession
        self.worldstate.session = self.aiosession
        self.steam_api.session = self.aiosession
        self.penguin_stats.session = self.aiosession

        forever.Utilities.session = self.aiosession
        
        self.basic_task = self.loop.create_task(self.basic_loop())
        print(discord.__version__)
        print(await self.application_info())
        
    async def on_guild_join(self, guild):
        #(self, server_id, discord_server, logchannel, updated_messages, notifications, joinable_roles, role_messages
        server = Server(guild.id, guild, None, {}, [], set(), {})
        self.database.runtime["servers"][guild.id] = server
        await self.database.create_server(guild.id)
    async def on_message(self, message):
        try:
            server = self.database.runtime.get("servers").get(message.guild.id)
            for key, module in self.commands.items():
                if message.content.startswith(module.command_key):
                    await module.parse(message, server)
                    break
            if server:
                if server.voice:
                    for i, f in server.voice.sounds.items():
                        if message.content == i:
                            await server.voice.playFile(f)
                            break
            if message.content.startswith(self.command_key+"help"):
                em = EmbedTemplate(title="Help", timestamp=datetime.utcnow())
                for name, commandset in self.commands.items():
                    em.add_field(name=f"{name.title()}", value=commandset.command_key+" help")
                await message.channel.send(embed=em)
        except Exception as e:
            log([f"[COMMANDS][{datetime.now().strftime('%Y-%m-%d, %H:%I:%S.%f')}] {e}", traceback.format_exc()+"\r\n"])
    async def on_voice_state_update(self, member, before, after):
        server = self.database.runtime["servers"].get(member.guild.id)
        if server and server.voice and len(server.voice.vc.channel.members) == 1:
            server.voice.playlist.clear()
            await server.voice.skip()
            await server.voice.vc.disconnect()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id != self.user.id:
            if payload.guild_id:
                server = self.database.runtime.get("servers").get(payload.guild_id)
                if server:
                    if payload.message_id in server.joinable_roles["reactions"] and str(payload.emoji) == server.joinable_roles["reactions"][payload.message_id]["emoji"]:
                        member = await server.discord_server.fetch_member(payload.user_id)
                        await member.add_roles(server.joinable_roles["id"][server.joinable_roles["reactions"][payload.message_id]["role_id"]])

    async def on_raw_reaction_remove(self, payload):
        if payload.user_id != self.user.id:
            if payload.guild_id:
                server = self.database.runtime.get("servers").get(payload.guild_id)
                if server:
                    if payload.message_id in server.joinable_roles["reactions"] and str(payload.emoji) == server.joinable_roles["reactions"][payload.message_id]["emoji"]:
                        member = await server.discord_server.fetch_member(payload.user_id)
                        await member.remove_roles(server.joinable_roles["id"][server.joinable_roles["reactions"][payload.message_id]["role_id"]])

    async def on_raw_message_delete(self, payload):
        message = payload.cached_message
        if message:
            if message.id in self.database.saved_messages:
                await self.database.delete_updated_message(message.id)
                await self.database.delete_role_message(message.id)  
    async def on_raw_bulk_message_delete(self, payload):
        em = EmbedTemplate(title="Message Purge", description="{} message(s) were purged")
    async def on_message_edit(self, before, after):
        if before.author != self.user:
            if before != after:
                pass
    async def on_guild_channel_create(self, channel):
        pass
    async def on_guild_channel_delete(self, channel):
        pass
    async def on_guild_role_create(self, role):
        pass
    async def on_guild_role_delete(self, role):
        pass
    async def on_member_join(self, member):
        pass
    async def on_member_remove(self, member):
        pass
    async def on_member_update(self, before, after):
        pass
    async def on_member_ban(self, guild, user):
        pass


            
if __name__ == "__main__":
    bot = Bot()
    bot.run(config.token)