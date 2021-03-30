import discord
import asyncio
from datetime import datetime
import time
import traceback

import config

from models.EmbedTemplate import EmbedTemplate

from forever.Database import Database
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
        self.database = Database(config.host, config.user, config.password, config.database)
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
        self.basic_task = None
        self.database_task = None
    async def basic_loop(self,):
        await self.wait_until_ready()
        while True:
            try:
                await self.worldstate.getData(self.database.runtime)
                await self.newswire.getData()
                gtadata = {"gtanw" : self.newswire.nw_items.values()}
                data = {**gtadata, **self.worldstate.runtime}
                for i in self.database.runtime["servers"].values():
                    await asyncio.sleep(2)
                    await i.updateMessages(data, self.database)
                        
            except Exception as e:
                print("Error, logged")
                log(["[BASE LOOP][{}] {}".format(time.time(), e), traceback.format_exc()+"\n\n"])

            await asyncio.sleep(60)
    async def database_loop(self,):
        await self.wait_until_ready()
        while True:
            await asyncio.sleep(3)
            if self.database.runtime["servers"]:
                for x in self.guilds:
                    if x.id not in [i.server_id for i in self.database.runtime["servers"].values()]:
                        tmp = Server(x.id, x, None, {}, [], [])
                        self.database.objectToQuery(tmp)
                        self.database.runtime["servers"][x.id] = tmp
                for x in self.database.runtime["servers"].values():
                    if x.server_id not in [i.id for i in self.guilds]:
                        self.database.queryToDB(x.delete())
                    if x.voice != None:
                        x.voice.updateSounds()
            await asyncio.sleep(10)
    async def on_ready(self,):
        print("Everythings ready")
        print(discord.__version__)
        print(await self.application_info())
        await self.database.initRuntime(self)
        self.database_task = self.loop.create_task(self.database_loop())
        self.basic_task = self.loop.create_task(self.basic_loop())
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
        voice_client = next((i for i in self.voice_clients if i.guild.id == member.guild.id), None)
        if voice_client != None:
            if len(voice_client.channel.members) == 1:
                await voice_client.disconnect()
    async def on_raw_message_delete(self, payload):
        message = payload.cached_message
    async def on_raw_bulk_message_delete(self, payload):
        if len(payload.message_ids) == len(payload.cached_messages):
            message = payload.cached_messages
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