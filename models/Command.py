import discord
class Command:
    def __init__(self, commandKey, name, description, usage, aliases):
        self.aliases = aliases
        self.commandKey = commandKey
        self.name = name
        self.description = description
        self.usage = usage

        self.aliases.append(self.name)