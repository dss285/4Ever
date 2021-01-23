import asyncio
import discord
from forever.CrissCross import CrissCross as CC
from forever.Newswire import Newswire
from forever.NewswireMessage import NewswireMessage
from models.Commands import Commands
from models.Command import Command
from models.EmbedTemplate import EmbedTemplate
import re

class ForeverCommands(Commands):
    def __init__(self, moduleName, description, commandKey, client, database, newswire):
        self.client = client
        self.database = database
        self.newswire = newswire
        commandlist = self.fetchCommands(commandKey)
        super().__init__(moduleName, commandlist, description, commandKey)

    def fetchCommands(self, commandKey):
        commandlist = {}
        commandlist["list"] = ListRoles(commandKey)
        commandlist["join"] = Join(commandKey)
        commandlist["leave"] = Leave(commandKey)
        commandlist["add"] = Add(commandKey, self.database)
        commandlist["remove"] = Remove(commandKey, self.database)
        commandlist["crisscross"] = CrissCross(commandKey, self.client)
        commandlist["gtanw"] = GTANewswire(commandKey, self.database, self.newswire)
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
        if message.author.guild_permissions.administrator:
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
        if message.author.guild_permissions.administrator:
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
class CrissCross(Command):
    def __init__(self, commandKey, client):
        self.client = client
        super().__init__(commandKey, "crisscross", """Start a game of crisscross""", "{} {} {}".format(commandKey, "crisscross", "*<challenged user>*"), [])
    async def run(self, message, server):
        pattern = re.escape(self.commandKey)+"\s("+"|".join(self.aliases)+")\s(?:<@!?(?:\d+)>)\s?(\d{1,2})?"
        reg = re.match(pattern, message.content)
        if reg:
            if len(message.mentions) == 1:
                user = message.mentions[0]
                await message.channel.send("Would you like to accept this challenge ? (y) for yes, and anything to reject")
                response = await self.client.wait_for('message', timeout=30.0, check=lambda x: x.author == user and x.channel == message.channel)
                if "y" in response.content.lower():
                    size = 3
                    if reg.group(2):
                        size = int(reg.group(2))
                    game = CC(message.author, response.author, self.client, size)
                    await game.StartGame(message.channel)
                else:
                    await message.channel.send("Challenge denied.")
            else:
                await message.channel.send("Only 1 user may be challenged at once.")
class GTANewswire(Command):
    def __init__(self, commandKey, database, newswire):
        self.database = database
        self.newswire = newswire
        super().__init__(commandKey, "gtanw", """GTA V newswire""", "{} {}".format(commandKey, "gtanw"), [])
    async def run(self, message, server):
        pattern = re.escape(self.commandKey)+"\s("+"|".join(self.aliases)+")\s?(message)?"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                em = EmbedTemplate(title="WorldState Message", description="Updating soon..")
                msg = await message.channel.send(embed=em)
                nwmessage = NewswireMessage(msg)
                self.database.objectToDB(nwmessage)
            else:
                x = 5
                posts = await self.newswire.getEmbeds(x)
                for i in posts:
                    await message.channel.send(embed=i)
                    x+=1
