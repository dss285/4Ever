import discord
class EmbedTemplate(discord.Embed):
    def __init__(self, *args, **kwargs):
        if "color" not in kwargs:
            kwargs["color"] = 0x8A00E0
        super().__init__(*args, **kwargs)