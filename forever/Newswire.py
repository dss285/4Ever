import aiohttp
import discord
import asyncio
import json
import time
class Newswire:
	def __init__(self,):
		self.time = 0
		self.posted_ids = set()
		self.last_list = None
	async def getData(self, limit=5):
		xx = time.time()
		if xx-self.time > 3600:
			async with aiohttp.ClientSession() as sess:
				async with sess.get("https://www.rockstargames.com/graph.json?operationName=NewswireList&variables=%7B%22cache%22%3Atrue%2C%22tagId%22%3Anull%2C%22page%22%3A1%2C%22metaUrl%22%3A%22%2Fnewswire%22%2C%22locale%22%3A%22en_us%22%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%2283496aa1837be901d129c3532af6fc2d5627df190d58cb730d2073f519d1d95c%22%7D%7D") as r:
					if r.status == 200:
						parsing = await r.text()
						parsedjson = json.loads(parsing)['data']['posts']['results']
						posts = []
						x = 0
						for i in parsedjson:
							if x <= limit:
								primaryid = i['primary_tags'][0]['id']
								if primaryid == 702:
									posts.append(i)
									x+=1
							else:
								break
						for i in range(len(posts)):
							if posts[i]['id'] not in self.posted_ids:
								image = posts[i]['preview_images_parsed']['newswire_block']['square']
								em = discord.Embed(
									title=posts[i]['title'], 
									description="https://www.rockstargames.com/newswire/article/{}".format(posts[i]['id']))
								em.set_image(url=image)
								self.posted_ids.add(posts[i]['id'])
								posts[i] = em
						self.last_list = posts[::-1]
						return self.last_list
		else:
			return self.last_list
						
if __name__ == '__main__':
	nw = Newswire()
	loop = asyncio.get_event_loop()
	loop.run_until_complete(nw.getData())
	loop.close()