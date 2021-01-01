import discord
import asyncio
import time
from datetime import datetime

from forever.Utilities import Utilities
from abstract.UpdatedMessage import UpdatedMessage
from abstract.EmbedTemplate import EmbedTemplate

class NewswireMessage(UpdatedMessage):
    def __init__(self, message):
        super().__init__(message, "gtanw")
    async def refresh(self, newswire_data):
        em = EmbedTemplate(title="GTA V Newswire", timestamp=datetime.utcnow(), inline=False)
        x = 1
        for i in newswire_data:
            em.add_field(name="**{}**. {}...".format(x, i.title[:15]), value="[{}]({})\n\n[{}]({})\n".format(
                "Link",
                i.url,
                "Image",
                i.image
            ))
            x+=1
        await self.message.edit(embed=em)