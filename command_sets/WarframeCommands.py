import asyncio
import discord
import time
from models.Commands import Commands
from models.Command import Command
from models.EmbedTemplate import EmbedTemplate

from forever.Warframe import DropTables, CetusMessage, SortieMessage, FissureMessage, InvasionMessage, NightwaveMessage
import re

class WarframeCommands(Commands):
    def __init__(self, module_name, description, command_key, client, database):
        self.database = database
        self.client = client
        self.droptables = DropTables()
        command_list = self.fetchCommands(command_key)
        super().__init__(module_name, command_list, description, command_key)

    def fetchCommands(self, command_key):
        command_list = {}
        command_list["worldstate"] = WorldState(command_key, self.database)
        command_list["relics"] = RelicSearch(command_key, self.droptables, self.client)
        return command_list
class WorldState(Command):
    def __init__(self, command_key, database):
        self.database = database
        super().__init__(command_key, "worldstate", """Creates an message where X thing is updated from Warframe Worldstate""", "{} {} {}".format(command_key, "worldstate", "*<nightwave|sorties|poe|invasions|fissures>*"), ["worldstate"])
    async def run(self, message, server):
        if message.author.guild_permissions.administrator:
            pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")\s(nightwave|sorties|poe|invasions|fissures)"
            reg = re.match(pattern, message.content)
            if reg:
                em = EmbedTemplate(title="WorldState Message", description="Updating soon..")
                if reg.group(2):
                    new_message = None
                    msg_type = None
                    msg = await message.channel.send(embed=em)
                    if reg.group(2) == "nightwave":
                        new_message = NightwaveMessage(msg)
                        
                    elif reg.group(2) == "sorties":
                        new_message = SortieMessage(msg)
                    elif reg.group(2) == "fissures":
                        new_message = FissureMessage(msg, [])
                    elif reg.group(2) == "poe":
                        new_message = CetusMessage(msg, [])
                    elif reg.group(2) == "invasions":
                        new_message = InvasionMessage(msg, [])
                    if new_message:
                        
                        msg_type = reg.group(2)
                        await self.database.create_updated_message(server.server_id, msg_type, msg.channel.id, msg.id)
                        server.updated_messages["name"][msg_type] = new_message
                        server.updated_messages["id"][msg.id] = new_message
class RelicSearch(Command):
    def __init__(self, command_key, droptables, client):
        self.client = client
        self.droptables = droptables
        super().__init__(command_key, "relic", """Relic search""", "{} {} {}".format(command_key, "relic", "*<relicname>*"), ["relicsearch"])
    async def run(self, message, server):
        pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")\s(.*)"
        reg = re.match(pattern, message.content)
        xx = time.time()
        if reg:
            if not self.droptables.data or xx-self.droptables.timeupdated > self.droptables.interval:
                asyncio.create_task(self.droptables.getData())
            while not self.droptables.data:
                await asyncio.sleep(3)
            await message.channel.send(embed=self.droptables.relicSearch(reg.group(2)))


