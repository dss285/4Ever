from abstract.EmbedTemplate import EmbedTemplate
import datetime
class Doll:
    def __init__(self, doll_id, name, doll_type, rarity, formation_bonus, formation_tiles, skill, aliases, productiontimer=None):
        self.doll_id = doll_id
        self.name = name
        self.doll_type = doll_type
        self.rarity = rarity
        self.formation_bonus = formation_bonus
        self.formation_tiles = formation_tiles
        self.skill = skill
        self.aliases = aliases
        self.productiontimer = productiontimer
    def getImagePath(self,):
        path = "/home/dss/project/website/www/assets/gfl/dolls"
        return "{}/128x167_{}.png".format(path, self.name.replace(" ", "_").replace("/",""))
    def getEmbed(self,):
        em = EmbedTemplate(title=self.name)
        if self.productiontimer:
            em.add_field(name="Production time", value="{}".format(datetime.timedelta(seconds=self.productiontimer)), inline=False)
        
        em.add_field(name="Skill", value=self.skill if self.skill else "N/A")
        if self.formation_bonus and self.formation_tiles:
            formationtiles = self.formation_tiles.replace("0", "⬛").replace("1", "⬜").replace("2", "🟦")
            em.add_field(name="Formation", value="{}\n\n{}".format(formationtiles, self.formation_bonus), inline=False)
        return em




