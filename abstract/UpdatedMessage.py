#!/usr/bin/python
import discord
class UpdatedMessage:
    def __init__(self, message, message_type):
        self.message = message
        self.message_type = message_type
    def refresh(self,):
        raise NotImplementedError
    def sql(self,):
        sql = """INSERT INTO discord_updated_messages (server_id, message_type, message_channel_id, message_id) VALUES ({}, "{}", {}, {}) ON DUPLICATE KEY UPDATE message_id={}""".format(
            self.message.guild.id,
            self.message_type,
            self.message.channel.id,
            self.message.id,
            self.message.id
        )
        return sql
    def delete(self,):
        sql = """DELETE FROM discord_updated_messages WHERE message_id={}""".format(
            self.message.id
        )
        return sql

