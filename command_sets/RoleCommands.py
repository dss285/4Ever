import asyncio
import discord
from models.Commands import Commands
from models.Command import Command
from models.EmbedTemplate import EmbedTemplate
import re

class RoleCommands(Commands):
    def __init__(self, module_name, description, command_key, client, database):
        self.client = client
        self.database = database
        command_list = self.fetchCommands(command_key)
        super().__init__(module_name, command_list, description, command_key)

    def fetchCommands(self, command_key):
        command_list = {}
        command_list["list"] = ListRoles(command_key)
        command_list["join"] = Join(command_key)
        command_list["leave"] = Leave(command_key)
        command_list["add"] = Add(command_key, self.database)
        command_list["remove"] = Remove(command_key, self.database)
        return command_list
class Join(Command):
    def __init__(self, command_key):
        super().__init__(command_key, "join", """Joins X role""", "{} {} {}".format(command_key, "join", "*<role name>*"), [])
    async def run(self, message, server):
        pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")\s(.+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                if message.role_mentions:
                    for i in message.role_mentions:
                        if i in server.joinable_roles["set"]:
                            message.author.add_roles(i)
                elif reg.group(2) in server.joinable_roles["name"]:
                    await message.author.add_roles(server.joinable_roles["name"][reg.group(2)])
                elif reg.group(2) in server.joinable_roles["id"]:
                    await message.author.add_roles(server.joinable_roles["id"][reg.group(2)])
class Leave(Command):
    def __init__(self, command_key):
        super().__init__(command_key, "leave", """Leaves X role""", "{} {} {}".format(command_key, "leave", "*<role name>*"), [])
    async def run(self, message, server):
        pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")\s(.+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                if message.role_mentions:
                    for i in message.role_mentions:
                        if i in server.joinable_roles["set"]:
                            await message.author.remove_roles(i)
                elif reg.group(2) in server.joinable_roles["name"]:
                    await message.author.add_roles(server.joinable_roles["name"][reg.group(2)])
                elif reg.group(2) in server.joinable_roles["id"]:
                    await message.author.add_roles(server.joinable_roles["id"][reg.group(2)])
class Add(Command):
    def __init__(self, command_key, database):
        self.database = database
        super().__init__(command_key, "add", """Adds X role""", "{} {} {}".format(command_key, "add", "*<role mention>*"), [])
    async def run(self, message, server):
        if message.author.guild_permissions.administrator:
            pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")\s(.+)"
            reg = re.match(pattern, message.content)
            if reg:
                if reg.group(2):
                    for i in message.role_mentions:
                        if i not in server.joinable_roles["set"]:
                            sql = """INSERT INTO discord_joinable_roles (role_id, server_id) VALUES ({}, {})""".format(
                                i.id,
                                server.server_id
                            )
                            self.database.queryToDB(sql)
                            server.joinable_roles["set"].add(i)
                            server.joinable_roles["id"][i.id] = i
                            server.joinable_roles["name"][i.name] = i
                        
class Remove(Command):
    def __init__(self, command_key, database):
        self.database = database
        super().__init__(command_key, "remove", """Removes X role""", "{} {} {}".format(command_key, "remove", "*<role mention>*"), [])
    async def run(self, message, server):
        if message.author.guild_permissions.administrator:
            pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")\s(.+)"
            reg = re.match(pattern, message.content)
            if reg:
                if reg.group(2):
                    for i in message.role_mentions:
                        if i in server.joinable_roles["set"]:
                            sql = "DELETE FROM discord_joinable_roles WHERE role_id={} AND server_id={}".format(
                                i.id,
                                server.server_id
                            )
                            self.database.queryToDB(sql)
                            server.joinable_roles["set"].remove(i)
                            del server.joinable_roles["id"][i.id]
                            del server.joinable_roles["name"][i.name]
class ListRoles(Command):
    def __init__(self, command_key):
        super().__init__(command_key, "list", """Lists roles""", "{} {}".format(command_key, "list"), [])
    async def run(self, message, server):
        pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")"
        reg = re.match(pattern, message.content)
        if reg:
            em = EmbedTemplate(title="Role list", description="\n".join(server.joinable_roles["name"].keys()))
            await message.channel.send(embed=em)