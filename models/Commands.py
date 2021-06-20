from models.EmbedTemplate import EmbedTemplate
class Commands:
    def __init__(self, module_name, command_list, description, command_key):
        self.module_name = module_name
        self.command_key = command_key
        self.command_list = command_list
        self.description = description
        self.help_embed = self.__help()

    def __help(self,):
        desc_string = self.description+"\n\n"
        for i in self.command_list.values():
            desc_string += """
            **Command:**
            {} {}  -  {}
            **Usage:**
            {}
            **Aliases:**
            ```{}```
            """.format(self.command_key, i.name, i.description, i.usage, ",".join(i.aliases))
        embed = EmbedTemplate(title=self.module_name, description=desc_string)
        return embed
    async def parse(self, message, server):
        if message.content.startswith("{} {}".format(self.command_key, "help")):
            await message.channel.send(embed=self.help_embed)
        else:
            tobreak = False
            for i, command in self.command_list.items():
                if tobreak:
                    break
                for x in command.aliases:
                    if message.content.startswith("{} {}".format(self.command_key, x)):
                        await command.run(message, server)
                        tobreak = True
                        break
                if tobreak:
                    break

class Command:
    def __init__(self, command_key, name, description, usage, aliases):
        self.aliases = aliases
        self.command_key = command_key
        self.name = name
        self.description = description
        self.usage = usage

        self.aliases.append(self.name)