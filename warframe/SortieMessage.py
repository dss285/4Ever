import discord
import asyncio
import time
from datetime import datetime
from models.UpdatedMessage import UpdatedMessage
from models.EmbedTemplate import EmbedTemplate

from warframe.SolSystem import SolPlanet, SolNode
class SortieItem:
    def __init__(self, start_time, expiry_time, missions):
        self.start_time = start_time
        self.expiry_time = expiry_time
        self.missions = missions

class SortieMission:
    def __init__(self, missionType, node, modifier):
        self.missionType = missionType
        self.node = node
        self.modifier = modifier
    def __str__(self,):
        if type(self.node) == str:
            return "{}\n{}\n{}".format(self.missionType, self.node, self.modifier)
        return "{}\n{}\n{}".format(self.missionType, self.node.name.title()+", "+self.node.planet.name.title(), self.modifier)

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