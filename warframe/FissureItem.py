from warframe.SolNode import SolNode
from warframe.SolPlanet import SolPlanet
from forever import Utilities
import time
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
        return "{}\n{}\nExpires in {:.0f} min".format(
            self.node.planet.name.title()+", "+self.node.name.title(), 
            "Expires on {}".format(Utilities.ts2string(self.expiry_time)),
            self.expiresIn()//60
            )