import asyncio
import aiohttp
import discord
from voice.VoicePlayer import VoicePlayer
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
        queries = []
        delete_types = []
        for message_id, message in self.updated_messages["id"].items():
            try:
                await message.refresh(data[message.message_type])
            except discord.NotFound:
                queries.extend(self.delete_message(message.message))
                delete_types.append(message_id)
        for i in queries:
            db.queryToDB(i)
        for x in delete_types:
            del self.updated_messages["name"][x]

    def return_ids(self,):
        pass
        # tmp = {
        #     "server_id" : self.server_id,
        #     "logchannel_id" : self.logchannel.id if self.logchannel else None,
        #     "updated_messages_ids" : {},
        #     "joinable_roles_ids" : [x.id for x in self.joinable_roles],
        #     "notifications_ids" : {}
        # }
        # for message_type, i in self.updated_messages.items():
        #     tmp["updated_messages_ids"][i.message_type] = i.message.id
        # for i in self.notifications:
        #     tmp["notifications_ids"][i.name] = i.role.id
        # return tmp
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
    def delete_message(self, message):
        queries = []
        if message.id in self.updated_messages["id"]:
            queries.append("DELETE FROM discord_updated_messages WHERE message_id={}".format(message.id))
        if message.id in self.joinable_roles["reactions"]:
            queries.append("DELETE FROM discord_role_messages WHERE message_id={}".format(message.id))
        return queries
    def __repr__(self):
        return "<Forever.Server discord_server={}>".format(self.discord_server.__repr__())