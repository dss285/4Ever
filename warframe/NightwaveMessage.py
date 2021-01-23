import discord
import asyncio
import time
from datetime import datetime
from forever.Utilities import Utilities
from warframe.NightwaveItem import NightwaveItem
from models.UpdatedMessage import UpdatedMessage
from models.EmbedTemplate import EmbedTemplate
class NightwaveMessage(UpdatedMessage):
    def __init__(self, message):
        super().__init__(message, "nightwave")

    async def refresh(self, nightwave_data):
        em = EmbedTemplate(title="Nightwave", timestamp=datetime.utcnow())
        for i in nightwave_data:
            em.add_field(name=i.name, value=(Utilities.ts2string(i.start_time+(60*120))+"\n\n"))
        
        await self.message.edit(embed=em)
