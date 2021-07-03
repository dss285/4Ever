import discord
class EmbedTemplate(discord.Embed):
    def __init__(self, *args, **kwargs):
        if "color" not in kwargs:
            kwargs["color"] = 0x2F3136
        super().__init__(*args, **kwargs)