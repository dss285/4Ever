from warframe.SolPlanet import SolPlanet
from warframe.SolNode import SolNode
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