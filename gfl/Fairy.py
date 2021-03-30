from models.EmbedTemplate import EmbedTemplate
import datetime
class Fairy:
    def __init__(self, fairy_id, name, stats, skill, production_timer):
        self.fairy_id = fairy_id
        self.name = name
        self.stats = stats.split("|")
        self.skill = skill
        self.production_timer = production_timer
    def getEmbed(self,):
        em = EmbedTemplate(title=self.name)
        if self.production_timer:
            em.add_field(
                name="Production Time",
                value="{}".format(datetime.timedelta(seconds=self.production_timer)),
                inline=False
            )
        if self.stats:
            em.add_field(name="Stats", value="\n".join(self.stats))
        em.add_field(name="Skill", value=self.skill if self.skill else "N/A")
        
        return em