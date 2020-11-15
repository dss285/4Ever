from abstract.Command import Command
from abstract.EmbedTemplate import EmbedTemplate
class Commands:
    def __init__(self, moduleName, commandList, description, commandKey):
        self.moduleName = moduleName
        self.commandKey = commandKey
        self.commandList = commandList
        self.description = description
        self.help_embed = self.__help()

    def __help(self,):
        desc_string = self.description+"\n\n"
        for i in self.commandList.values():
            desc_string += "{} {}  -  {}\nUsage: {}\n\n".format(self.commandKey, i.name, i.description, i.usage)
        embed = EmbedTemplate(title=self.moduleName, description=desc_string)
        return embed
    async def parse(self, message, server):
        if message.content.startswith("{} {}".format(self.commandKey, "help")):
            await message.channel.send(embed=self.help_embed)
        else:
            tobreak = False
            for i, command in self.commandList.items():
                if tobreak:
                    break
                for x in command.aliases:
                    if message.content.startswith("{} {}".format(self.commandKey, x)):
                        await command.run(message, server)
                        tobreak = True
                        break
                if tobreak:
                    break

