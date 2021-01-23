import discord
import asyncio
import time
from datetime import datetime
from warframe.FissureItem import FissureItem
from models.UpdatedMessage import UpdatedMessage
from models.EmbedTemplate import EmbedTemplate

class FissureMessage(UpdatedMessage):
    def __init__(self, message, mentions):
        super().__init__(message, "fissures")
        self.mentions = mentions
    async def refresh(self, fissures):
        em = EmbedTemplate(title="Fissures", timestamp=datetime.utcnow())
        for i in fissures:
            em.add_field(name="{} {}".format(i.era, i.mission_type), value=str(i))
        await self.message.edit(embed=em)