import asyncio
import aiohttp
import discord
from forever.Voice import VoicePlayer
from models.UpdatedMessage import UpdatedMessage
class Server:
    def __init__(self, server_id, discord_server, logchannel, updated_messages, notifications, joinable_roles, role_messages):
        self.server_id = server_id
        self.discord_server = discord_server
        self.logchannel = logchannel
        self.updated_messages = {"name" : updated_messages}
        self.updated_messages["id"] = {}
        
        self.notifications = notifications
        self.joinable_roles = {"set":joinable_roles}
        self.joinable_roles["id"] = {}
        self.joinable_roles["name"] = {}
        self.joinable_roles["reactions"] =role_messages
        for i in self.joinable_roles["set"]:
            self.joinable_roles["id"][i.id] = i
            self.joinable_roles["name"][i.name] = i
        for i, j in updated_messages.items():
            self.updated_messages["id"][j.message.id] = j

        self.voice = None
    async def updateMessages(self, data, db):
        for message_id, message in self.updated_messages["id"].items():
            try:
                await message.refresh(data[message.message_type])

            except discord.NotFound:
                pass
    def __repr__(self):
        return "<Forever.Server discord_server={}>".format(self.discord_server.__repr__())