import discord
import asyncio
from datetime import datetime
import time
import traceback

import config

from models.EmbedTemplate import EmbedTemplate

from forever.Database import Database_Manager
from forever.Server import Server
from forever.Newswire import Newswire
from warframe.Worldstate import Worldstate
from warframe.DropTables import DropTables

from command_sets.VoiceCommands import VoiceCommands
from command_sets.ModerationCommands import ModerationCommands
from command_sets.MathCommands import MathCommands
from command_sets.WarframeCommands import WarframeCommands
from command_sets.ForeverCommands import ForeverCommands
from command_sets.GFLCommands import GFLCommands
from command_sets.NSFWCommands import NSFWCommands
from command_sets.RoleCommands import RoleCommands
from command_sets.BotAdminCommands import BotAdminCommands

class Bot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.database = Database_Manager(config.host, config.user, config.password, config.database)
        self.worldstate = Worldstate()
        self.newswire = Newswire()
        self.command_key = "\u0024"
        self.commands = {
            "botadmin" :    BotAdminCommands("Bot Admin", "", self.command_key+"botadmin", self, self.database),
            "voice" :       VoiceCommands("Voice", "This module has all the voice commands related to the bot", self.command_key+"voice", self),
            "moderation" :  ModerationCommands("Moderation", "This module has all the moderation commands related to the bot", self.command_key+"mod"),
            "role" :        RoleCommands("Role", "This module has all the role commands", self.command_key+"role", self, self.database),
            "math" :        MathCommands("Math", "This module has math commands", self.command_key+"math", self),
            "warframe" :    WarframeCommands("Warframe", "Warframe module", self.command_key+"wf", self, self.database),
            "forever" :     ForeverCommands("Forever", "Main module of the bot", self.command_key+"fe", self, self.database, self.newswire),
            "gfl" :         GFLCommands("Girls' Frontline", "GFL Module", self.command_key+"gfl", self, self.database),
            "nsfw" :        NSFWCommands("NSFW", "NSFW Module", self.command_key+"nsfw")
        }
        self.basic_task = self.loop.create_task(self.basic_loop())
    async def basic_loop(self,):
        await self.wait_until_ready()
        await self.database.init_runtime(self)
        while True:
            try:
                guilds = set(self.guilds)

                                    
                for x in self.guilds:
                    if x.id not in self.database.runtime["servers"]:
                        tmp = Server(x.id, x, None, {}, [], set(), {})
                        self.database.create_server(x.id)
                        self.database.runtime["servers"][x.id] = tmp
                
                for i, j in self.database.runtime["servers"].items():
                    if i not in guilds:
                        self.database.delete_server(i)
                    if j.voice != None:
                        j.voice.update_sounds()
                await self.worldstate.getData(self.database.runtime)
                await self.newswire.getData()
                gtadata = {"gtanw" : self.newswire.nw_items.values()}
                data = {**gtadata, **self.worldstate.runtime}
                await asyncio.sleep(2)
                for i in self.database.runtime["servers"].values():
                    self.loop.create_task(i.updateMessages(data, self.database))
            except Exception as e:
                print("Error, logged")
                log(["[BASE LOOP][{}] {}".format(time.time(), e), traceback.format_exc()+"\n\n"])

            await asyncio.sleep(120)
    async def on_ready(self,):
        print("Everythings ready")
        print(discord.__version__)
        print(await self.application_info())
        
        
    async def on_guild_join(self, guild):
        #(self, server_id, discord_server, logchannel, updated_messages, notifications, joinable_roles, role_messages
        server = Server(guild.id, guild, None, {}, [], set(), {})
        self.database.runtime["servers"][guild.id] = server
        self.database.create_server(guild.id)
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
                    em.add_field(name="{}".format(name.title()), value=commandset.command_key+" help")
                await message.channel.send(embed=em)
        except Exception as e:
            print("Error, logged")
            log(["[COMMANDS][{}] {}".format(time.time(), e), traceback.format_exc()+"\n\n"])
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
                self.database.delete_updated_message(message.id)
                self.database.delete_role_message(message.id)


        
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

def log(messages, file="log.txt"):
    fo = open("log.txt", "a+")
    for i in messages:
        fo.write(i)
    fo.close()
            
if __name__ == "__main__":
    bot = Bot()
    bot.run(config.token)