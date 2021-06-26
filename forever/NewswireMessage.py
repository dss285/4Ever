import discord
import asyncio
import time
import aiohttp
import json
from datetime import datetime

from forever import Utilities
from models.UpdatedMessage import UpdatedMessage
from models.EmbedTemplate import EmbedTemplate
class Newswire:
	def __init__(self,):
		self.time = 0
		self.nw_items = {}
	async def getData(self, limit=5):
		xx = time.time()
		if xx-self.time > 3600:
			async with aiohttp.ClientSession() as sess:
				async with sess.get("https://graph.rockstargames.com/?query=query%20NewswireList(%24locale%3A%20String!%2C%20%24page%3A%20Int!%2C%20%24tagId%3A%20Int%2C%20%24metaUrl%3A%20String!%2C%20%24cache%3A%20Boolean%20%3D%20true)%20%7B%0A%20%20meta%3A%20metaUrl(url%3A%20%24metaUrl%2C%20domain%3A%20%22www%22%2C%20locale%3A%20%24locale)%20%7B%0A%20%20%20%20title%0A%20%20%20%20__typename%0A%20%20%7D%0A%20%20posts(page%3A%20%24page%2C%20tagId%3A%20%24tagId%2C%20locale%3A%20%24locale)%20%7B%0A%20%20%20%20paging%20%7B%0A%20%20%20%20%20%20...paging%0A%20%20%20%20%20%20__typename%0A%20%20%20%20%7D%0A%20%20%20%20results%20%7B%0A%20%20%20%20%20%20...postFields%0A%20%20%20%20%20%20__typename%0A%20%20%20%20%7D%0A%20%20%20%20__typename%0A%20%20%7D%0A%7D%0A%0Afragment%20postFields%20on%20RockstarGames_Newswire_Model_Entity_Post%20%7B%0A%20%20id%0A%20%20title%0A%20%20name_slug%0A%20%20created%0A%20%20created_formatted%0A%20%20primary_tags%20%7B%0A%20%20%20%20id%0A%20%20%20%20name%0A%20%20%20%20__typename%0A%20%20%7D%0A%20%20preview_images_parsed%20%7B%0A%20%20%20%20newswire_block%20%7B%0A%20%20%20%20%20%20square%0A%20%20%20%20%20%20d16x9%0A%20%20%20%20%20%20_fallback%0A%20%20%20%20%20%20__typename%0A%20%20%20%20%7D%0A%20%20%20%20__typename%0A%20%20%7D%0A%20%20__typename%0A%7D%0A%0Afragment%20paging%20on%20RockstarGames_Cake_Graph_Type_Paging%20%7B%0A%20%20pageCount%0A%20%20page%0A%20%20count%0A%20%20nextPage%0A%20%20prevPage%0A%20%20perPage%0A%20%20__typename%0A%7D%0A&operationName=NewswireList&variables=%7B%22tagId%22%3Anull%2C%22page%22%3A1%2C%22metaUrl%22%3A%22%2Fnewswire%22%2C%22locale%22%3A%22en_us%22%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22cdc02dfaa8ee1e39ec54b910138fe17e3c9062c1c34feb9628b7213211fa0cc5%22%7D%7D") as r:
					if r.status == 200:
						parsing = await r.text()
						parsedjson = json.loads(parsing)['data']
						if parsedjson:
							parsedjson = parsedjson['posts']['results']
							posts = []
							x = 0
							for i in parsedjson:
								if x < limit:
									if i['primary_tags']:
										primaryid = i['primary_tags'][0]['id']
										if primaryid == 702:
											posts.append(i)
											x+=1
								else:
									break
							for i in posts:
								self.nw_items[i['id']] = NewswireItem(
									i['id'],
									i['title'],
									f"https://www.rockstargames.com/newswire/article/{i['id']}",
									i['preview_images_parsed']['newswire_block']['square'])
							self.time = time.time()
		else:
			return self.nw_items
	async def getEmbeds(self, limit=5):
		await self.getData(limit)
		embeds = []
		for i in self.nw_items.values():
			embeds.append(i.toEmbed())
		return embeds
class NewswireItem:
	def __init__(self, id, title, url, image):
		self.id = id
		self.title = title
		self.url = url
		self.image = image
	def toEmbed(self,):
		em = EmbedTemplate(
			title=self.title, 
			description=self.url)
		em.set_image(url=self.image)
		return em
class NewswireMessage(UpdatedMessage):
    def __init__(self, message):
        super().__init__(message, "gtanw")
    async def refresh(self, newswire_data):
        em = EmbedTemplate(title="GTA V Newswire", timestamp=datetime.utcnow(), inline=False)
        x = 1
        for i in newswire_data:
            em.add_field(name=f"**{x}**. {i.title[:15]}...",
			value=f"[Link]({i.url})\n\n[Image]({i.image})\n")
            x+=1
        await self.message.edit(embed=em)