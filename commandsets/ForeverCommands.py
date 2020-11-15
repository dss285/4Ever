import asyncio
import discord
from abstract.Commands import Commands
from abstract.Command import Command
from abstract.EmbedTemplate import EmbedTemplate
import re

class ForeverCommands(Commands):
    def __init__(self, moduleName, description, commandKey, client, database):
        self.client = client
        self.database = database
        commandlist = self.fetchCommands(commandKey)
        super().__init__(moduleName, commandlist, description, commandKey)

    def fetchCommands(self, commandKey):
        commandlist = {}
        commandlist["list"] = ListRoles(commandKey)
        commandlist["join"] = Join(commandKey)
        commandlist["leave"] = Leave(commandKey)
        commandlist["add"] = Add(commandKey, self.database)
        commandlist["remove"] = Remove(commandKey, self.database)
        return commandlist
class Join(Command):
    def __init__(self, commandKey):
        super().__init__(commandKey, "join", """Joins X role""", "{} {} {}".format(commandKey, "join", "*<role name>*"), [])
    async def run(self, message, server):
        pattern = re.escape(self.commandKey)+"\s("+"|".join(self.aliases)+")\s(.+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                for i in server.joinable_roles:
                    if str(i) == reg.group(2):
                        await message.author.add_roles(i)
                        break
class Leave(Command):
    def __init__(self, commandKey):
        super().__init__(commandKey, "leave", """Leaves X role""", "{} {} {}".format(commandKey, "leave", "*<role name>*"), [])
    async def run(self, message, server):
        pattern = re.escape(self.commandKey)+"\s("+"|".join(self.aliases)+")\s(.+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                for i in server.joinable_roles:
                    if str(i) == reg.group(2):
                        await message.author.remove_roles(i)
                        break
class Add(Command):
    def __init__(self, commandKey, database):
        self.database = database
        super().__init__(commandKey, "add", """Adds X role""", "{} {} {}".format(commandKey, "add", "*<role>*"), [])
    async def run(self, message, server):
        pattern = re.escape(self.commandKey)+"\s("+"|".join(self.aliases)+")\s(.+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                if len(message.role_mentions) == 1:
                    sql = """INSERT INTO discord_joinable_roles (role_id, server_id) VALUES ({}, {})""".format(
                        message.role_mentions[0].id,
                        server.server_id
                    )
                    self.database.queryToDB(sql)
class Remove(Command):
    def __init__(self, commandKey, database):
        self.database = database
        super().__init__(commandKey, "remove", """Removes X role""", "{} {} {}".format(commandKey, "remove", "*<role name>*"), [])
    async def run(self, message, server):
        pattern = re.escape(self.commandKey)+"\s("+"|".join(self.aliases)+")\s(.+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                for i in server.joinable_roles:
                    if str(i) == reg.group(2):
                        sql = "DELETE FROM discord_joinable_roles WHERE role_id={} AND server_id={}".format(
                            i.id,
                            server.server_id
                        )
                        self.database.queryToDB(sql)
class ListRoles(Command):
    def __init__(self, commandKey):
        super().__init__(commandKey, "list", """Lists roles""", "{} {}".format(commandKey, "list"), [])
    async def run(self, message, server):
        pattern = re.escape(self.commandKey)+"\s("+"|".join(self.aliases)+")"
        reg = re.match(pattern, message.content)
        if reg:
            em = EmbedTemplate(title="Role list", description="\n".join([str(x) for x in server.joinable_roles]))
            await message.channel.send(embed=em)
