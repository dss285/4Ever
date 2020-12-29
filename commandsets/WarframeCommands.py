import asyncio
import discord
import time
from abstract.Commands import Commands
from abstract.Command import Command
from abstract.EmbedTemplate import EmbedTemplate

from warframe.DropTables import DropTables
from warframe.CetusMessage import CetusMessage
from warframe.SortieMessage import SortieMessage
from warframe.FissureMessage import FissureMessage
from warframe.InvasionMessage import InvasionMessage
from warframe.NightwaveMessage import NightwaveMessage
import re

class WarframeCommands(Commands):
    def __init__(self, moduleName, description, commandKey, client, database):
        self.database = database
        self.client = client
        self.droptables = DropTables()
        commandlist = self.fetchCommands(commandKey)
        super().__init__(moduleName, commandlist, description, commandKey)

    def fetchCommands(self, commandKey):
        commandlist = {}
        commandlist["worldstate"] = WorldState(commandKey, self.database)
        commandlist["relics"] = RelicSearch(commandKey, self.droptables, self.client)
        return commandlist
class WorldState(Command):
    def __init__(self, commandKey, database):
        self.database = database
        super().__init__(commandKey, "worldstate", """Creates an message where X thing is updated from Warframe Worldstate""", "{} {} {}".format(commandKey, "worldstate", "*<nightwave|sorties|poe|invasions|fissures>*"), ["worldstate"])
    async def run(self, message, server):
        if message.author.guild_permissions.administrator:
            pattern = re.escape(self.commandKey)+"\s("+"|".join(self.aliases)+")\s(nightwave|sorties|poe|invasions|fissures)"
            reg = re.match(pattern, message.content)
            if reg:
                em = EmbedTemplate(title="WorldState Message", description="Updating soon..")
                if reg.group(2):
                    new_message = None
                    msg = await message.channel.send(embed=em)
                    if reg.group(2) == "nightwave":
                        new_message = NightwaveMessage(msg)
                    elif reg.group(2) == "sorties":
                        new_message = SortieMessage(msg)
                    elif reg.group(2) == "fissures":
                        new_message = FissureMessage(msg)
                    elif reg.group(2) == "poe":
                        new_message = CetusMessage(msg)
                    elif reg.group(2) == "invasions":
                        new_message = InvasionMessage(msg)
                    if new_message:
                        self.database.objectToDB(new_message)
class RelicSearch(Command):
    def __init__(self, commandKey, droptables, client):
        self.client = client
        self.droptables = droptables
        super().__init__(commandKey, "relic", """Relic search""", "{} {} {}".format(commandKey, "relic", "*<relicname>*"), ["relicsearch"])
    async def run(self, message, server):
        pattern = re.escape(self.commandKey)+"\s("+"|".join(self.aliases)+")\s(.*)"
        reg = re.match(pattern, message.content)
        xx = time.time()
        if reg:
            if not self.droptables.data or xx-self.droptables.timeupdated > self.droptables.interval:
                asyncio.create_task(self.droptables.getData())
            while not self.droptables.data:
                await asyncio.sleep(3)
            await message.channel.send(embed=self.droptables.relicSearch(reg.group(2)))


