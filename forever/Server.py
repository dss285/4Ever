import asyncio
import aiohttp
import discord
from voice.VoicePlayer import VoicePlayer
from models.UpdatedMessage import UpdatedMessage
class Server:
    def __init__(self, server_id, discord_server, logchannel, updated_messages, notifications, joinable_roles):
        self.server_id = server_id
        self.discord_server = discord_server
        self.logchannel = logchannel
        self.updated_messages = updated_messages
        self.notifications = notifications
        self.joinable_roles = {"set":joinable_roles}
        self.joinable_roles["id"] = {}
        self.joinable_roles["name"] = {}
        for i in self.joinable_roles["set"]:
            self.joinable_roles["id"][i.id] = i
            self.joinable_roles["name"][i.name] = i
        self.voice = None
    async def updateMessages(self, data, db):
        removekeys = []
        for message_type, message in self.updated_messages.items():
            try:
                await message.refresh(data[message_type])
            except discord.NotFound:
                removekeys.append(message_type)
                db.queryToDB(message.delete())
        for i in removekeys:
            del self.updated_messages[i]
    def return_ids(self,):
        tmp = {
            "server_id" : self.server_id,
            "logchannel_id" : self.logchannel.id if self.logchannel else None,
            "updated_messages_ids" : {},
            "joinable_roles_ids" : [x.id for x in self.joinable_roles],
            "notifications_ids" : {}
        }
        for message_type, i in self.updated_messages.items():
            tmp["updated_messages_ids"][i.message_type] = i.message.id
        for i in self.notifications:
            tmp["notifications_ids"][i.name] = i.role.id
        return tmp
    def sql(self,):
        if self.logchannel:
            return "INSERT INTO discord_server (serverid, logchannel_id) VALUES ({server}, {log}) ON DUPLICATE KEY UPDATE logchannel_id={log}".format(
                server=self.server_id,
                log=self.logchannel.id
            )
        else:
            return "INSERT INTO discord_server (serverid) VALUES ({server}) ON DUPLICATE KEY IGNORE".format(
                server=self.server_id
            )
    def delete(self,):
        return "DELETE FROM discord_server WHERE server_id={server}".format(
            server=self.server_id
        )
    def __repr__(self):
        return "<Forever.Server discord_server={}>".format(self.discord_server.__repr__())