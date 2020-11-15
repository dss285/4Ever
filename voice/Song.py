import discord
import datetime
import time
from abstract.EmbedTemplate import EmbedTemplate
class Song():
    def __init__(self, duration, views, title, url, voice):
        self.duration = duration
        self.views = views
        self.title = title
        self.url = url
        self.voice = voice
        self.played = False
    def returnEmbed(self,):
        em = EmbedTemplate(title=self.title, timestamp=datetime.datetime.utcnow())
        em.add_field(name="Duration", value="{}".format(
            time.gmtime(self.duration)
        ))
        em.add_field(name="Views", value="{}".format(self.views))
        return em