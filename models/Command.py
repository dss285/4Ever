import discord
class Command:
    def __init__(self, command_key, name, description, usage, aliases):
        self.aliases = aliases
        self.command_key = command_key
        self.name = name
        self.description = description
        self.usage = usage

        self.aliases.append(self.name)