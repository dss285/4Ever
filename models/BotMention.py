import discord
import asyncio
from models.Timer import Timer
class BotMention:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.message = None
        self.timer = None
    async def check(self):
        if self.message is not None:
            if self.timer != None:
                if self.timer.isExpired():
                    await self.message.delete()
                    self.timer = None
                    self.message = None
    async def send_mention(self, channel, timer):
        if self.role:
            self.timer = timer
            self.message = await channel.send("{} - {}".format(self.name, self.role.mention))
                
