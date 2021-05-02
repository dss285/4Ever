import discord
import asyncio
import time
from datetime import datetime
from warframe.InvasionItem import InvasionItem
from models.UpdatedMessage import UpdatedMessage
from models.EmbedTemplate import EmbedTemplate
class InvasionMessage(UpdatedMessage):
    def __init__(self, message, mentions):
        super().__init__(message, "invasions")
        self.mentions = mentions
    async def refresh(self, invasions):
        em = EmbedTemplate(title="Invasions", timestamp=datetime.utcnow())
        for i in invasions:
            vals = []
            if type(i.node) == str:
                vals.append("{}, {}".format(i.node.title(), i.node.title()))
            else:
                vals.append("{}, {}".format(i.node.planet.name.title(), i.node.name.title())) 
            vals.append(i.start_time)
            vals.append("{} vs {}".format(i.defender.faction,i.attacker.faction)),
            vals.append(i.status)

            em.add_field(
            name="{} vs {}".format(i.defender.rewards, i.attacker.rewards), 
            value="{}\n{}\n{}\n{}\n\u200b".format(*vals
            ))
        await self.message.edit(embed=em)