import discord
import asyncio
import time
from datetime import datetime

from forever import Utilities
from models.UpdatedMessage import UpdatedMessage
from models.EmbedTemplate import EmbedTemplate

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