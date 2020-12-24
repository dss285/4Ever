from bs4 import BeautifulSoup
import aiohttp
import asyncio
import re
import time
import discord
import json
class DropTables:
	def __init__(self,):
		self.data = {}
		self.timeupdated = 0
	async def getData(self,):
		xx = time.time()
		if xx - self.timeupdated > 43200: #12h
			self.timeupdated = time.time()
			async with aiohttp.ClientSession() as sess:
				async with sess.get("https://n8k6e2y6.ssl.hwcdn.net/repos/hnfvc0o3jnfvc873njb03enrf56.html") as r:
					if r.status==200:
						parsing = await r.text()
						reg = re.findall("<h3 id=\"(\w+)\">(.*?)<\/h3>\s*<table>([\s\S]*?)<\/table>", parsing, re.MULTILINE|re.DOTALL)
						for i in reg:
							parser = BeautifulSoup(i[2], 'html.parser')
							table_rows = parser.find_all('tr')
							self.data[i[0]] = {}
							self.data[i[0]]["title"] = i[1].replace(":", "")
							self.data[i[0]]["data"] = []
							test = {}
							if i[0] == "missionRewards" or i[0] == "keyRewards" or i[0] == "transientRewards":
								tmp_mission = None
								tmp_rotation = None
								for x in table_rows:
									text = x.get_text()
									if x.select('th') and "Rotation" not in text:
										tmp_mission = text
										tmp_rotation = None
										test[tmp_mission] = {}
									elif "Rotation" in text:
										tmp_rotation = text
										test[tmp_mission][tmp_rotation] = []
									else:
										if tmp_rotation:
											test[tmp_mission][tmp_rotation].append(text)
										elif "data" in test[tmp_mission]:
											test[tmp_mission]["data"].append(text)
										else:
											test[tmp_mission]["data"] = []
											test[tmp_mission]["data"].append(text)
								self.data[i[0]]["data"] = test
							if i[0] == "relicRewards":
								relicname = None
								rarity = None
								for x in table_rows:
									text = x.get_text()
									if "Relic" in text:
										relic_match = re.match("((?:Axi|Neo|Meso|Lith|Requiem)\s\w{0,3}\d{0,2}\s?Relic)\s\((Radiant|Exceptional|Flawless|Intact)\)", text)
										if relic_match.group(1) in test:
											if relic_match.group(2) not in test[relic_match.group(1)]:
												test[relic_match.group(1)][relic_match.group(2)] = []
												rarity = relic_match.group(2)
										else:
											test[relic_match.group(1)] = {}
											test[relic_match.group(1)][relic_match.group(2)] = []
											rarity = relic_match.group(2)
											relicname = relic_match.group(1)
									else:
										test[relicname][rarity].append(text)
							if i[0] == "sortieRewards":
								test = []
								for x in table_rows:
									text = x.get_text()
									if not x.select('th'):
										test.append(text)
							if i[0] == "cetusRewards" or i[0] == "solarisRewards" or i[0] == "deimosRewards":
								test = {}
								bounty = None
								stage = None
								rotation = None
								for x in table_rows:
									text = x.get_text()
									if x.select('th'):
										if "Bounty" in text:
											bounty = text
											test[bounty] = {}
										elif "Rotation" in text:
											rotation = text
											test[bounty][rotation] = {}
										elif "Stage" in text:
											stage = text
											test[bounty][rotation][stage] = []
									else:
										test[bounty][rotation][stage].append(text)
							if i[0] in ["modByAvatar", "blueprintByAvatar", "resourceByAvatar", "sigilByAvatar", "additionalItemByAvatar"]:
								drop = None
								for x in table_rows:
									text = x.get_text()
									itemtitles = re.match(r"^([\s\S]+?)(?:Additional Item|Mod|Resource|Blueprint\/Item|Sigil) Drop Chance: (\d{0,3}\.\d{0,3})\%$", text)
									if itemtitles:
										drop = itemtitles.group(1)
										test[drop] = {}
										test[drop]["chance"] = itemtitles.group(2)
										test[drop]["data"] = []
									else:
										test[drop]["data"].append(text)
							if i[0] in ["modByDrop", "blueprintByDrop", "resourceByDrop"]:
								drop = None
								for x in table_rows:
									text = x.get_text()
									if x.select('th'):
										if "Source" not in text:
											drop = text
											test[drop] = []
									else:
										test[drop].append(text)
							self.data[i[0]]["data"] = test
	def searchKey(self, key, searched_value):
		vals = []
		for i in self.data[key]["data"]:
			if i.lower().startswith(searched_value.lower()):
				vals.append(i)
		return vals
	def relicSearch(self, searched_value):
		vals = self.searchKey("relicRewards", searched_value)
		if len(vals) == 1:
			em = discord.Embed(title=self.data["relicRewards"]["title"], description=vals[0])
			for i, j in self.data["relicRewards"]["data"][vals[0]].items():
				em.add_field(name=i, value="\n".join(j))
			return em
		else:
			return discord.Embed(title=self.data["relicRewards"]["title"], description="\n".join(vals))



if __name__ == '__main__':
	droptables = DropTables()
	loop = asyncio.get_event_loop()
	loop.run_until_complete(droptables.getData())
	loop.close()