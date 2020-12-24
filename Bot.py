import discord
import asyncio
from datetime import datetime
import time
import traceback
import config

from abstract.EmbedTemplate import EmbedTemplate

from forever.Database import Database
from forever.Server import Server
from warframe.Worldstate import Worldstate
from warframe.DropTables import DropTables

from commandsets.VoiceCommands import VoiceCommands
from commandsets.ModerationCommands import ModerationCommands
from commandsets.MathCommands import MathCommands
from commandsets.WarframeCommands import WarframeCommands
from commandsets.ForeverCommands import ForeverCommands
from commandsets.GFLCommands import GFLCommands
from commandsets.NSFWCommands import NSFWCommands
class Bot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.database = Database("localhost", "dss285", "aeon123", "aeon")
        self.worldstate = Worldstate()
        self.commandKey = "\u0024"
        self.commands = {
            "voice" :       VoiceCommands("Voice", "This module has all the voice commands related to the bot", self.commandKey+"voice", self),
            "moderation" :  ModerationCommands("Moderation", "This module has all the moderation commands related to the bot", self.commandKey+"mod"),
            "math" :        MathCommands("Math", "This module has math commands", self.commandKey+"math", self),
            "warframe" :    WarframeCommands("Warframe", "Warframe module", self.commandKey+"wf", self, self.database),
            "forever" :     ForeverCommands("Forever", "Main module of the bot", self.commandKey+"fe", self, self.database),
            "gfl" :         GFLCommands("Girls' Frontline", "GFL Module", self.commandKey+"gfl", self, self.database),
            "nsfw" :        NSFWCommands("NSFW", "NSFW Module", self.commandKey+"nsfw")
        }
        self.basic_task = None
        self.database_task = None
        
    async def basic_loop(self,):
        await self.wait_until_ready()
        while True:
            try:
                await self.worldstate.getData(self.database.runtime)
                for i in self.database.runtime["servers"]:
                    await asyncio.sleep(2)
                    await i.updateMessages(self.worldstate.runtime)
            except Exception as e:
                print("[BASE LOOP] {}".format(e))
                print(traceback.format_exc())
            await asyncio.sleep(60)
    async def database_loop(self,):
        await self.wait_until_ready()
        while True:
            
            await self.database.update_runtime(self)
            
            await asyncio.sleep(3)
            if self.database.runtime["servers"]:
                for x in self.guilds:
                    if x.id not in [i.server_id for i in self.database.runtime["servers"]]:
                        tmp = Server(x.id, x, None, {}, [], [])
                        self.database.objectToQuery(tmp)
                for x in self.database.runtime["servers"]:
                    if x.server_id not in [i.id for i in self.guilds]:
                        self.database.queryToDB(x.delete())
                    if x.voice != None:
                        x.voice.updateSounds()
            await asyncio.sleep(10)
    async def on_ready(self,):
        print("Everythings ready")
        print(discord.__version__)
        print(await self.application_info())
        await self.database.translateToObjects(self)
        self.database_task = self.loop.create_task(self.database_loop())
        self.basic_task = self.loop.create_task(self.basic_loop())
    async def on_message(self, message):
        try:
            server = next((x for x in self.database.runtime["servers"] if message.guild.id == x.server_id), None)
            for key, module in self.commands.items():
                if message.content.startswith(module.commandKey):
                    await module.parse(message, server)
            if server:
                if server.voice:
                    for i, f in server.voice.sounds.items():
                        if message.content == i:
                            await server.voice.playFile(f)
                            break
            if message.content.startswith(self.commandKey+"help"):
                em = EmbedTemplate(title="Help", timestamp=datetime.utcnow())
                for name, commandset in self.commands.items():
                    em.add_field(name="{}".format(name.title()), value=commandset.commandKey+" help")
                await message.channel.send(embed=em)
        except Exception as e:
            print("[COMMANDS] {}".format(e))
            print(traceback.format_exc())
    async def on_voice_state_update(self, member, before, after):   
        voice_client = next((i for i in self.voice_clients if i.guild.id == member.guild.id), None)
        if voice_client != None:
            if len(voice_client.channel.members) == 1:
                await voice_client.disconnect()

                
            
if __name__ == "__main__":
    bot = Bot()
    bot.run(config.token)