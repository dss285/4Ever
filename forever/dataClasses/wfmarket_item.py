import aiohttp
import socket
import json
class wfmarket_item:
	def __init__(self,urlname):
		self.urlname = urlname
	async def get_Data(self,):
		headers = {"Platform":"pc","Language":"en"}
		connector = aiohttp.TCPConnector(family=socket.AF_INET,verify_ssl=False)
		async with aiohttp.ClientSession(headers=headers,connector=connector) as session:
			async with session.get("https://api.warframe.market/v1/items/"+self.urlname+"/statistics") as r:
				if r.status==200:
					var = await r.text()
					var = json.loads(var)
					buys = []
					sell = []
					for i in var["payload"]["statistics_live"]["48hours"]:
						if i['order_type'] == "buy":
							buys.append(i["avg_price"])
						elif i['order_type'] == "sell":
							sell.append(i["avg_price"])
					sumb = 0
					sums = 0
					if len(buys) != 0:
						sumb = sum(buys)/len(buys)
					if len(sell) != 0:
						sums = sum(sell)/len(sell)
					return [int(sumb),int(sums)]