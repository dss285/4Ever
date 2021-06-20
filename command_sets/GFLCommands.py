import asyncio
import discord
import re
import datetime

from models.EmbedTemplate import EmbedTemplate
from models.Commands import Commands, Command


class GFLCommands(Commands):
    def __init__(self, module_name, description, command_key, client, database):
        self.client = client
        self.database = database
        command_list = self.fetchCommands(command_key)
        super().__init__(module_name, command_list, description, command_key)
    def fetchCommands(self, command_key):
        command_list = {}
        command_list["production"] = ProductionDolls(command_key, self.client, self.database)
        command_list["doll"] = DollInfo(command_key, self.client, self.database)
        return command_list
class ProductionDolls(Command):
    def __init__(self, command_key, client, database):
        self.client = client
        self.database = database
        super().__init__(command_key, "production", """Production Dolls""", "{} {}".format(command_key, "production"), ["production","prod", "pr"])
    async def run(self, message, server):
        pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")"
        reg = re.match(pattern, message.content)
        if reg:
            tmp = self.database.runtime["gfl"]["dolls"]
            tmp = [x for x in tmp if x.production_timer]
            tmp_str = []
            
            for doll in sorted(tmp, key=lambda x: x.production_timer):
                tmp_str.append("{} {} {}".format(datetime.timedelta(seconds=doll.production_timer), doll.name, doll.doll_type))
            lists = [tmp_str[i:i+30] for i in range(0, len(tmp_str), 30)]
            em = EmbedTemplate(title="Production Dolls")
            for i in lists:
                em.add_field(name="PRODUCTION", value="\n".join(i), inline=True)
            await message.channel.send(embed=em)
class DollInfo(Command):
    def __init__(self, command_key, client, database):
        self.client = client
        self.database = database
        super().__init__(command_key, "doll", """Info of dolls""", "{} {}".format(command_key, "doll"), ["d", "tdoll"])
    async def run(self, message, server):
        pattern = re.escape(self.command_key)+"\s("+"|".join(self.aliases)+")\s(.+)"
        reg = re.match(pattern, message.content)
        if reg:
            if reg.group(2):
                doll = next((x for x in self.database.runtime["gfl"]["dolls"] if reg.group(2).lower() == x.name.lower() or reg.group(2).lower() in x.aliases), None)
                if doll:
                    em = doll.getEmbed()
                    image = discord.File(doll.getImagePath(), filename="doll.png")
                    em.set_image(url="attachment://doll.png")
                    await message.channel.send(file=image, embed=em)




