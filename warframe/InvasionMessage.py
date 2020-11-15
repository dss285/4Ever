import discord
import asyncio
import time
from datetime import datetime
from warframe.InvasionItem import InvasionItem
from abstract.UpdatedMessage import UpdatedMessage
from abstract.EmbedTemplate import EmbedTemplate
class InvasionMessage(UpdatedMessage):
    def __init__(self, message, mentions):
        super().__init__(message, "invasions")
        self.mentions = mentions
    async def refresh(self, invasions):
        em = EmbedTemplate(title="Invasions", timestamp=datetime.utcnow())
        for i in invasions:
            em.add_field(
            name="{} vs {}".format(i.defender.rewards, i.attacker.rewards), 
            value="{}\n{}\n{}\n{}\n\u200b".format(
                i.node.planet.name.title()+", "+i.node.name.title(),
                i.start_time,
                "{} vs {}".format(i.defender.faction,i.attacker.faction),
                i.status
            ))
        await self.message.edit(embed=em)