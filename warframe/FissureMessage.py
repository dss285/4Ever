import discord
import asyncio
import time
from datetime import datetime
from models.UpdatedMessage import UpdatedMessage
from models.EmbedTemplate import EmbedTemplate
from warframe.SolSystem import SolNode, SolPlanet
from forever import Utilities
class FissureItem:
    def __init__(self, oid, start_time, expiry_time, mission_type, node, era):
        self.start_time = start_time
        self.expiry_time = expiry_time
        self.mission_type = mission_type
        self.node = node
        self.era = era
    def expiresIn(self,):
        return self.expiry_time-time.time()
    def __str__(self,):
        if type(self.node) == str:
            return "{}\n{}\nExpires in {:.0f} min".format(
            self.node.title()+", "+self.node.title(), 
            "Expires on {}".format(Utilities.ts2string(self.expiry_time)),
            self.expiresIn()//60
            )
        return "{}\n{}\nExpires in {:.0f} min".format(
            self.node.planet.name.title()+", "+self.node.name.title(), 
            "Expires on {}".format(Utilities.ts2string(self.expiry_time)),
            self.expiresIn()//60
            )
class FissureMessage(UpdatedMessage):
    def __init__(self, message, mentions):
        super().__init__(message, "fissures")
        self.mentions = mentions
    async def refresh(self, fissures):
        em = EmbedTemplate(title="Fissures", timestamp=datetime.utcnow())
        for i in fissures:
            em.add_field(name="{} {}".format(i.era, i.mission_type), value=str(i))
        await self.message.edit(embed=em)
