import asyncio
import discord

from forever import Utilities
from models.EmbedTemplate import EmbedTemplate
from models.Commands import Commands, Command
from forever.Utilities import Args
import re

class RoleCommands(Commands):
    def __init__(self, module_name, description, command_key, client, database):
        self.client = client
        self.database = database
        command_list = self.fetch_commands(command_key)
        super().__init__(module_name, command_list, description, command_key)

    def fetch_commands(self, command_key):
        command_list = {}
        command_list["list"] = ListRoles(command_key)
        command_list["join"] = Join(command_key)
        command_list["leave"] = Leave(command_key)
        command_list["add"] = Add(command_key, self.database)
        command_list["remove"] = Remove(command_key, self.database)
        command_list["rolemessage"] = CreateRoleMessage(command_key, self.database, self.client)
        return command_list
class Join(Command):
    def __init__(self, command_key):
        super().__init__(command_key, "join", """Joins X role""", f"{command_key} join *<role name>*", [])
        self.args = Args(role=Args.ANY_ARG)
        self.args.set_pattern(command_key, self.aliases)
    async def run(self, message, server):
        parse = self.args.parse(message.content)
        if parse:
            if message.role_mentions:
                for i in message.role_mentions:
                    if i in server.joinable_roles["set"]:
                        message.author.add_roles(i)
            elif parse["role"] in server.joinable_roles["name"]:
                await message.author.add_roles(server.joinable_roles["name"][parse["role"]])
            elif parse["role"] in server.joinable_roles["id"]:
                await message.author.add_roles(server.joinable_roles["id"][parse["role"]])
class Leave(Command):
    def __init__(self, command_key):
        super().__init__(command_key, "leave", """Leaves X role""", f"{command_key} leave *<role name>*", [])
        self.args = Args(role=Args.ANY_ARG)
        self.args.set_pattern(command_key, self.aliases)
    async def run(self, message, server):
        parse = self.args.parse(message.content)
        if parse:
            if message.role_mentions:
                for i in message.role_mentions:
                    if i in server.joinable_roles["set"]:
                        await message.author.remove_roles(i)
            elif parse["role"] in server.joinable_roles["name"]:
                await message.author.add_roles(server.joinable_roles["name"][parse["role"]])
            elif parse["role"] in server.joinable_roles["id"]:
                await message.author.add_roles(server.joinable_roles["id"][parse["role"]])
class Add(Command):
    def __init__(self, command_key, database):
        self.database = database
        super().__init__(command_key, "add", """Adds X role""", f"{command_key} add *<role mention>*", [])
        self.args = Args(role=Args.ANY_ARG)
        self.args.set_pattern(command_key, self.aliases)
    async def run(self, message, server):
        if message.author.guild_permissions.administrator:
            parse = self.args.parse(message.content)
            if parse:
                for i in message.role_mentions:
                    if i not in server.joinable_roles["set"]:
                        await self.database.create_joinable_role(i.id, server.server_id)
                        server.joinable_roles["set"].add(i)
                        server.joinable_roles["id"][i.id] = i
                        server.joinable_roles["name"][i.name] = i                      
class Remove(Command):
    def __init__(self, command_key, database):
        self.database = database
        super().__init__(command_key, "remove", """Removes X role""", f"{command_key} remove *<role mention>*", [])
        self.args = Args(role=Args.ANY_ARG)
        self.args.set_pattern(command_key, self.aliases)
    async def run(self, message, server):
        if message.author.guild_permissions.administrator:
            parse = self.args.parse(message.content)
            if parse:
                for i in message.role_mentions:
                    if i in server.joinable_roles["set"]:
                        await self.database.delete_joinable_role(i.id)
                        server.joinable_roles["set"].remove(i)
                        del server.joinable_roles["id"][i.id]
                        del server.joinable_roles["name"][i.name]
class ListRoles(Command):
    def __init__(self, command_key):
        super().__init__(command_key, "list", """Lists roles""", f"{command_key} list", [])
        self.args = Args()
        self.args.set_pattern(command_key, self.aliases)
    async def run(self, message, server):
        parse = self.args.parse(message.content)
        if parse:
            em = EmbedTemplate(title="Role list", description="\n".join(server.joinable_roles["name"].keys()))
            await message.channel.send(embed=em)
class CreateRoleMessage(Command):
    def __init__(self, command_key, database, client):
        self.client = client
        self.database = database
        super().__init__(command_key, "rolemessage", """Assign role reaction to message or send new message to be reacted.""", f"{command_key} rolemessage *<channel mention>* *<role mention>*", [])
        self.args = Args(channel=Args.CHANNEL_MENTION_ARG, role=Args.MENTION_ARG)
        self.args.set_pattern(command_key, self.aliases)
    async def run(self, message, server):
        if message.author.guild_permissions.administrator:
            parse = self.args.parse(message.content)
            if parse:
                if message.channel_mentions and message.role_mentions:
                    channel = message.channel_mentions[0]
                    role = message.role_mentions[0]
                    try:
                        await message.channel.send("> Which style")
                        msg = await self.client.wait_for('message', check=lambda m: m.content in ['1', '2'] and m.author == message.author and m.channel == message.channel, timeout=60.0)
                        if msg and msg.content == '1': # Existing message to have role reaction
                            await message.channel.send("> Message ID, please")
                            messageid = await self.client.wait_for('message', check=lambda m: Utilities.is_int(m.content) and m.channel == message.channel and m.author == message.author, timeout=60.0)
                            if messageid:
                                try:
                                    role_msg = await channel.fetch_message(int(messageid.content))
                                    await message.channel.send("> Reaction to be assigned, react to this message.")
                                    reaction, user = await self.client.wait_for('reaction_add', check=lambda r, u: u.author == message.author, timeout=60.0)
                                    if user and reaction:
                                        server.joinable_roles["reactions"][role_msg.id] = {
                                            "message" : role_msg,
                                            "emoji" : str(reaction.emoji),
                                            "role_id" : role.id
                                        }
                                        await self.database.create_role_message(role.id, role_msg.id, channel.id, str(reaction.emoji), server.server_id)
                                        await role_msg.add_reaction(reaction.emoji)
                                except discord.NotFound:
                                    await message.channel.send("> Message couldn't be found")
                            else:
                                await message.channel.send("> Command execution failed, wrong input")                      
                        elif msg and msg.content == '2': # New message to have role reaction
                            pass
                        else:
                            await message.channel.send("> Command execution failed, wrong input")
                    except asyncio.TimeoutError:
                        await message.channel.send("> Too slow")
                    else:
                        await message.channel.send("> Command execution failed, wrong input")
