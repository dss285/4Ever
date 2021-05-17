class SolPlanet:
    def __init__(self, id, name):
        self.id = id
        self.name = name
class SolNode:
    def __init__(self, id, name, planet):
        self.id = id
        self.name = name
        self.planet = planet
