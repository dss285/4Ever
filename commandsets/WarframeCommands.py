import asyncio
import discord
from abstract.Commands import Commands
from abstract.Command import Command
from abstract.EmbedTemplate import EmbedTemplate

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
        commandlist = self.fetchCommands(commandKey)
        super().__init__(moduleName, commandlist, description, commandKey)

    def fetchCommands(self, commandKey):
        commandlist = {}
        commandlist["worldstate"] = WorldState(commandKey, self.database)
        return commandlist
class WorldState(Command):
    def __init__(self, commandKey, database):
        self.database = database
        super().__init__(commandKey, "worldstate", """Creates an message where X thing is updated from Warframe Worldstate""", "{} {} {}".format(commandKey, "worldstate", "*<nightwave|sorties|poe|invasions|fissures>*"), ["worldstate"])
    async def run(self, message, server):
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


