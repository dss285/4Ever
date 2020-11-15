import discord
import asyncio
import time
from datetime import datetime
import warframe.Sorties as Sorties
from abstract.UpdatedMessage import UpdatedMessage
from abstract.EmbedTemplate import EmbedTemplate

class SortieMessage(UpdatedMessage):
    def __init__(self, message):
        super().__init__(message, "sorties")
    async def refresh(self, sortie):
        em = EmbedTemplate(title="Sorties", timestamp=datetime.utcnow())
        count = 1
        for i in sortie.missions:
            em.add_field(name="Mission {}".format(count), value=str(i))
            count+=1
        await self.message.edit(embed=em)