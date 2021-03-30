from models.EmbedTemplate import EmbedTemplate
import config
import datetime
class Doll:
    def __init__(self, doll_id, name, doll_type, rarity, formation_bonus, formation_tiles, skill, aliases, production_timer=None):
        self.doll_id = doll_id
        self.name = name
        self.doll_type = doll_type
        self.rarity = rarity
        self.formation_bonus = formation_bonus
        self.formation_tiles = formation_tiles
        self.skill = skill
        self.aliases = aliases
        self.production_timer = production_timer
    def getImagePath(self,):
        return "{}/images/gfl/dolls/128x167_{}.png".format(config.asset_path, self.name.replace(" ", "_").replace("/",""))
    def getEmbed(self,):
        em = EmbedTemplate(title=self.name)
        if self.production_timer:
            em.add_field(name="Production Time", value="{}".format(datetime.timedelta(seconds=self.production_timer)), inline=False)
        
        em.add_field(name="Skill", value=self.skill if self.skill else "N/A")
        if self.formation_bonus and self.formation_tiles:
            formation_tiles = self.formation_tiles.replace("0", "⬛").replace("1", "⬜").replace("2", "🟦")
            em.add_field(
                name="Formation",
                value="{}\n\n{}".format(formation_tiles, self.formation_bonus),
                inline=False
            )
        return em
    def __repr__(self):
        return '<GFL.Doll name={}, id={}>'.format(self.name, self.doll_id)




