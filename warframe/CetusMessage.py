import discord
import asyncio
import time
from datetime import datetime
from warframe.CetusStatus import CetusStatus
from abstract.UpdatedMessage import UpdatedMessage
from abstract.EmbedTemplate import EmbedTemplate
from abstract.BotMention import BotMention
from abstract.Timer import Timer
class CetusMessage(UpdatedMessage):
    def __init__(self, message, mention):
        self.mention = mention
        super().__init__(message, "poe")
    async def refresh(self, cetus):
        em = EmbedTemplate(title="Plains of Eidolon", timestamp=datetime.utcnow())
        em.add_field(name="Status", value=str(cetus))
        em.add_field(name="Time until new rotation", value="{:.0f} min".format(cetus.minutesLeft()))
        await self.message.edit(embed=em)
        if (cetus.isNight() and self.mention and self.mention.message == None):
            await self.mention.send_mention(self.message.channel, Timer(cetus.expiry))
        if self.mention:
            await self.mention.check()

