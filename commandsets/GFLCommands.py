import asyncio
import discord
import re
import datetime

from models.EmbedTemplate import EmbedTemplate
from models.Commands import Commands
from models.Command import Command


class GFLCommands(Commands):
    def __init__(self, moduleName, description, commandKey, client, database):
        self.client = client
        self.database = database
        commandList = self.fetchCommands(commandKey)
        super().__init__(moduleName, commandList, description, commandKey)
    def fetchCommands(self, commandKey):
        commandList = {}
        commandList["production"] = ProductionDolls(commandKey, self.client, self.database)
        commandList["doll"] = DollInfo(commandKey, self.client, self.database)
        return commandList
class ProductionDolls(Command):
    def __init__(self, commandKey, client, database):
        self.client = client
        self.database = database
        super().__init__(commandKey, "production", """Production Dolls""", "{} {}".format(commandKey, "production"), ["production","prod", "pr"])
    async def run(self, message, server):
        pattern = re.escape(self.commandKey)+"\s("+"|".join(self.aliases)+")"
        reg = re.match(pattern, message.content)
        if reg:
            tmp = self.database.runtime["gfl"]["dolls"]
            tmp = [x for x in tmp if x.productiontimer]
            tmp_str = []
            
            for doll in sorted(tmp, key=lambda x: x.productiontimer):
                tmp_str.append("{} {} {}".format(datetime.timedelta(seconds=doll.productiontimer), doll.name, doll.doll_type))
            lists = [tmp_str[i:i+30] for i in range(0, len(tmp_str), 30)]
            em = EmbedTemplate(title="Production Dolls")
            for i in lists:
                em.add_field(name="PRODUCTION", value="\n".join(i), inline=True)
            await message.channel.send(embed=em)
class DollInfo(Command):
    def __init__(self, commandKey, client, database):
        self.client = client
        self.database = database
        super().__init__(commandKey, "doll", """Info of dolls""", "{} {}".format(commandKey, "doll"), ["d", "tdoll"])
    async def run(self, message, server):
        pattern = re.escape(self.commandKey)+"\s("+"|".join(self.aliases)+")\s(.+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                doll = next((x for x in self.database.runtime["gfl"]["dolls"] if reg.group(2).lower() == x.name.lower() or reg.group(2).lower() in x.aliases), None)
                if doll:
                    em = doll.getEmbed()
                    image = discord.File(doll.getImagePath(), filename="doll.png")
                    em.set_image(url="attachment://doll.png")
                    await message.channel.send(file=image, embed=em)




