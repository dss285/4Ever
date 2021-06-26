import asyncio
import discord
import time
from models.EmbedTemplate import EmbedTemplate
from models.Commands import Commands, Command

from forever.Warframe import DropTables, CetusMessage, SortieMessage, FissureMessage, InvasionMessage, NightwaveMessage
import re

class WarframeCommands(Commands):
    def __init__(self, module_name, description, command_key, client, database):
        self.database = database
        self.client = client
        self.droptables = DropTables()
        command_list = self.fetch_commands(command_key)
        super().__init__(module_name, command_list, description, command_key)

    def fetch_commands(self, command_key):
        command_list = {}
        command_list["worldstate"] = WorldState(command_key, self.database)
        command_list["relics"] = RelicSearch(command_key, self.droptables, self.client)
        return command_list
class WorldState(Command):
    UPDATED_MESSAGE_REGEX = "(?P<{}>nightwave|sorties|poe|invasions|fissures)"
    def __init__(self, command_key, database):
        self.database = database
        super().__init__(command_key, "worldstate", """Creates an message where X thing is updated from Warframe Worldstate""", f"{command_key} worldstate *<nightwave|sorties|poe|invasions|fissures>*", ["worldstate"])
        self.args = Args(message=WorldState.UPDATED_MESSAGE_REGEX)
        self.args.set_pattern(command_key, self.aliases)
    async def run(self, message, server):
        if message.author.guild_permissions.administrator:
            parse = self.args.parse(message.content)
            if parse:
                em = EmbedTemplate(title="WorldState Message", description="Updating soon..")
                new_message = None
                msg_type = None
                msg = await message.channel.send(embed=em)
                if parse.get("message") == "nightwave":
                    new_message = NightwaveMessage(msg)
                elif parse.get("message") == "sorties":
                    new_message = SortieMessage(msg)
                elif parse.get("message") == "fissures":
                    new_message = FissureMessage(msg, [])
                elif parse.get("message") == "poe":
                    new_message = CetusMessage(msg, [])
                elif parse.get("message") == "invasions":
                    new_message = InvasionMessage(msg, [])
                if new_message:
                    
                    msg_type = parse.get("message")
                    await self.database.create_updated_message(server.server_id, msg_type, msg.channel.id, msg.id)
                    server.updated_messages["name"][msg_type] = new_message
                    server.updated_messages["id"][msg.id] = new_message
class RelicSearch(Command):
    def __init__(self, command_key, droptables, client):
        self.client = client
        self.droptables = droptables
        super().__init__(command_key, "relic", """Relic search""", f"{command_key} relic *<relic name>*", ["relicsearch"])
        self.args = Args(relic=Args.ANY_ARG)
        self.args.set_pattern(command_key, self.aliases)
    async def run(self, message, server):
        parse = self.args.parse(message.content)
        xx = time.time()
        if parse:
            if not self.droptables.data or xx-self.droptables.timeupdated > self.droptables.interval:
                await self.droptables.getData()
            await message.channel.send(embed=self.droptables.relicSearch(parse.get("relic")))


