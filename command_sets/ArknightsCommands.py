import asyncio
from typing import Any, Union
import discord
import re
import datetime


from models.EmbedTemplate import EmbedTemplate
from models.Commands import Commands, Command
from models.Server import Server

from forever.Arknights import  Item, Stage
from forever.Database import DB_API
from forever.Utilities import Args, dict_search

class ArknightsCommands(Commands):
    def __init__(self, module_name : str, description : str, command_key : str, client : discord.Client, database : DB_API):
        self.client = client
        self.database = database
        command_list = self.fetch_commands(command_key)
        super().__init__(module_name, command_list, description, command_key)
    def fetch_commands(self, command_key : str):
        command_list = {}
        command_list["resourcesearch"] = ResourceSearch(command_key, self.client, self.database)

        return command_list
class ResourceSearch(Command):
    def __init__(self, command_key : str, client : discord.Client, database : DB_API):
        self.client = client
        self.database = database
        super().__init__(command_key, "resourcesearch", """Search AK resources, their sanitycosts /per stage""", f"{command_key} resourcesearch", ["rs", "resource", "item"])
        self.args = Args(resource=Args.ANY_ARG)
        self.args.set_pattern(command_key, self.aliases)
    async def run(self, message : discord.Message, server : Server):
        parsed = self.args.parse(message.content)
        if parsed:
            res = dict_search(self.database["arknights"]["items"]["names"], parsed["resource"])
            if res:
                if isinstance(res, str):
                    em = self.database["arknights"]["items"]["names"][res].get_embed()
                    await message.channel.send(embed=em)
                elif isinstance(res, list):
                    em = EmbedTemplate(title="Did you mean?", description="\n".join([f"{i}. {res[i-1]}" for i in range(1, len(res)+1)]))
                    await message.channel.send(embed=em)
                    msg = await self.client.wait_for('message', check=lambda x: x.author == message.author, timeout=30)
                    if msg:
                        if msg.content.isdigit():
                            tmp = int(msg.content)
                            if 1 <= tmp <= len(res):
                                em = self.database["arknights"]["items"]["names"][res[tmp-1]].get_embed()
                                await message.channel.send(embed=em)
            else: 
                em = EmbedTemplate(title="Not found", description="Resource wasn't found in the database, if you think this is an error, contact bot owner.")
                await message.channel.send(embed=em)