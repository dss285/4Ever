import discord
import asyncio
import time
from datetime import datetime
from forever import Utilities
from models.UpdatedMessage import UpdatedMessage
from models.EmbedTemplate import EmbedTemplate
class NightwaveItem:
    def __init__(self, start_time, expiry_time, name, daily=False):
        self.start_time = start_time
        self.expiry_time = expiry_time
        self.name = name
        self.daily = daily

class NightwaveMessage(UpdatedMessage):
    def __init__(self, message):
        super().__init__(message, "nightwave")

    async def refresh(self, nightwave_data):
        em = EmbedTemplate(title="Nightwave", timestamp=datetime.utcnow())
        for i in nightwave_data:
            em.add_field(name=i.name, value=(Utilities.ts2string(i.start_time+(60*120))+"\n\n"))
        
        await self.message.edit(embed=em)
