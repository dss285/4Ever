import discord
import asyncio
import time
from datetime import datetime
from warframe.CetusStatus import CetusStatus
from models.UpdatedMessage import UpdatedMessage
from models.EmbedTemplate import EmbedTemplate
from models.BotMention import BotMention
class CetusMessage(UpdatedMessage):
    def __init__(self, message, mention, client):
        self.mention = mention
        self.notify_message = None
        self.lock = False
        self.client = client
        super().__init__(message, "poe")
    async def refresh(self, cetus):
        em = EmbedTemplate(title="Plains of Eidolon", timestamp=datetime.utcnow())
        em.add_field(name="Status", value=str(cetus))
        em.add_field(name="Time until new rotation", value="{:.0f} min".format(cetus.minutes_left() if cetus else 0.00))
        await self.message.edit(embed=em)
        if not self.lock:
            if cetus.isNight() and self.mention:
                self.lock = True
                self.notify_message = await self.message.channel.send("{} - {}".format(self.mention.name, self.mention.role.mention))
                self.client.loop.call_later(cetus.seconds_left()+60, self.callback)
    def callback(self,):
        self.client.loop.create_task(self.remove_message())
        self.lock = False
    async def remove_message(self,):
        await self.notify_message.delete()
        self.notify_message = None

