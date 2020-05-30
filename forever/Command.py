import discord
class Command:
    def __init__(self, name, description):
        self.name = name
        self.description = description
    def run(self,):
        raise NotImplementedError