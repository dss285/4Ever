import re
import forever.database
import discord
import asyncio

class SimpleCommands:
    def __init__(self):
        folder = "/home/dss/data/"
        file_name = "database.json"
        self.commands = {
            "gfl" : show
        }
        self.database = {}
    
    def parse(self, message, key):
        reg = re.match(key+"(\w*)\s(.*)", message)
        if reg:
            if reg.group(2):
                lst = reg.group(2).split(" ")
                self.commands[reg.group(1)](lst, message)
    async def show(self, arr, message):
        currentarray = self.database
        for x in arr:
            currentarray = currentarray[x]
        em =         
