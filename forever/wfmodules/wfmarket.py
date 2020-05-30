import socket
import aiohttp
import asyncio
from forever.dataClasses.wfmarket_item import *
class wfmarket:
	def __init__(self,):
		self.wfitems = {}
	async def mapRelic(self,relic):
		relics = self.requestKeys("Relics")
		if relic in relics:
			temp = {}
			abouttobemapped = self.requestTable("Relics",relic.title())
			for i in abouttobemapped["Intact"]:
				split = re.split("Uncommon|Rare|Common",i)
				if "Neuroptics" in split[0] or "Chassis" in split[0] or "Systems" in split[0]:
					split[0] = split[0].replace(" Blueprint","")
				temp[split[0]] = await self.getPrice(split[0])
			return temp
	async def getPrice(self,itemname):
		if itemname in self.wfitems.keys():
			return await self.wfitems[itemname].get_Data()
	async def wfmarketList(self,):
		headers = {"Platform":"pc","Language":"en"}
		connector = aiohttp.TCPConnector(family=socket.AF_INET,verify_ssl=False)
		async with aiohttp.ClientSession(headers=headers,connector=connector) as session:
			async with session.get("https://api.warframe.market/v1/items") as r:
				if r.status==200:
					var = await r.text()
					var = json.loads(var)
					for i in var["payload"]["items"]:
						self.wfitems[i["item_name"]] = wfmarket_item(i["url_name"])
