import json
import re
import aiohttp
import time
import discord
import asyncio
nodes = []
itemsT = []
mission = []
tempmsg = []
tmplist = []
alertList = {}
keystodel = []
with open('classes/dicts/items.json') as f:
	itemsT = json.load(f)
with open('classes/dicts/nodes.json') as f:
	nodes = json.load(f)
with open('classes/dicts/mission.json') as f:
	mission = json.load(f)
class Mission:
	def __init__(self,faction, location, missiontype=None):
		number = 0
		self.faction = re.sub('FC', '',faction)
		self.planet = ""
		for i in nodes["nodes"]:
			if i["node_id"] == location:
				break
			number+=1
		self.node = nodes["nodes"][number]['name']
		for i in nodes['planets']:
			if i['planet_id'] == nodes["nodes"][number]['planet_id']:
				self.planet = i['name']
				break
		
		self.missiontype = mission[missiontype]
class Sortie:
	def __init__(self,mission,):
		self.mission = mission
class Alert:
	def __init__(self,mission, expirationdate, startdate, rewards):
		self.expirationdate = int(expirationdate)/1000
		self.startdate = int(startdate)/1000
		self.mission = mission
		self.duration = self.expirationdate-self.startdate
		self.items = ""
		self.expired = False
		itemCounted = False
		for i in rewards.keys():
			if i=="countedItems":
				self.items = rewards['countedItems']
				itemCounted = True
				break
			if i=="items":
				self.items = rewards['items']
				itemCounted = False
				break
		self. msg = str(rewards['credits'])+" Credits\n"
		for i in self.items:
			if itemCounted == True:
				if i["ItemType"] in itemsT.keys():
					self.msg += str(i["ItemCount"])+"x "+itemsT[i["ItemType"]]+"\n"
				else:
					with open("items.txt", "a") as f:
						f.write(i["ItemType"])
					lst = i["ItemType"].split("/")
					ch = lst[len(lst)-1]
					self.msg += str(i["ItemCount"])+"x "+ch+"\n"
			else:
				if i in itemsT.keys():
					self.msg += itemsT[i]+"\n"
				else:
					with open("items.txt", "a") as f:
						f.write(i)
					lst = i.split("/")
					ch = lst[len(lst)-1]
					self.msg += ch+"\n"
		self.msg += mission.planet.capitalize()+": "+mission.node.capitalize()+" - "+mission.missiontype.capitalize()+"\n"
		self.msg += time.strftime("%d.%m.%Y %H:%M:%S", time.gmtime(self.startdate+(60*120)))+" - "+time.strftime("%d.%m.%Y %H:%M:%S", time.gmtime(self.expirationdate+(60*120)))+"\n\n"
		if self.expirationdate < time.time():
			expired = True
	def isExpired(self,):
		if self.expirationdate+100 < time.time():
			self.expired = True
			return self.expired
		else:
			return False
class Invasion:
	def __init__(self,mission,rewards):
		self.mission = mission
		self.rewards = rewards
class warframe:
	async def getInfo(self,):
		try:
			with open('classes/dicts/items.json') as f:
				itemsT = json.load(f)
			with open('classes/dicts/nodes.json') as f:
				nodes = json.load(f)
			with open('classes/dicts/mission.json') as f:
				mission = json.load(f)
			async with aiohttp.get("http://content.warframe.com/dynamic/worldState.php") as r:
				if r.status==200:
					alertList = []
					cetusStatus = ""
					parsing = await r.text()
					parsing = json.loads(parsing)
					syndicates = parsing["SyndicateMissions"]
					expiryTime = None
					start = None
					for i in syndicates:
						if i["Tag"]=="CetusSyndicate":
							expiryTime=int(i["Expiry"]["$date"]["$numberLong"])/1000
							break
					if expiryTime != None:
						start = expiryTime-150*60
						currentTime = ((expiryTime-time.time())/60)
						cetusStatus = "Day" if currentTime>50 else "Night"
					alerts = parsing["Alerts"]
					for i in alerts:
						activationdate = 	i['Activation']["$date"]["$numberLong"]
						expirationdate = 	i['Expiry']["$date"]["$numberLong"]
						rewards = 			i['MissionInfo']["missionReward"]
						missiontype = 		i['MissionInfo']['missionType']
						faction = 			i['MissionInfo']['faction']
						location = 			i['MissionInfo']['location']
						minlev = 			i['MissionInfo']['minEnemyLevel']
						maxlev = 			i['MissionInfo']['maxEnemyLevel']
						mission = Mission(faction, location, missiontype)
						alertList.append(Alert(mission,expirationdate, activationdate, rewards))
			return [[cetusStatus,expiryTime,start],alertList]
		except aiohttp.ClientOSError:
			return None
	async def loop(self, client, msg,db):
		global tempmsg
		global tmplist
		global alertList
		global keystodel
		dicts = db.dicts
		kwargs = db.keywords
		with open('mentions.json') as f:
			mentions = json.load(f)
		wfinfo = await self.getInfo()
		tridolons = {}
		if wfinfo != None:
			for key,value in dicts.items():
				channel = ""
				if value["alertmsgs"]:
					for val in value["alertmsgs"]:
						msg = ""
						try:
							channel = client.get_channel(val[0])
						except discord.NotFound:
							sql = "DELETE FROM alertmessages WHERE messageid=%s AND channel_id=%s LIMIT 1"
							args = (val[1],val[0])
							db.delete(sql, args)
							continue
						msg1 = ""
						for i in wfinfo[1]:
							msg += i.msg
							for l,f in dicts[key]["binds"].items():
								if "tridolon" in l:
									tridolons[key] = f
									continue
								if l in i.msg.lower():
									found = False
									for j,k in alertList.items():
										if k[0].isExpired():
											keystodel.append(j)
											try:
												await client.delete_message(k[1])
											except:
												pass
											if f in k[1].content:
												found = True
												break
									if found == False:
										if key not in alertList.keys():
											msgs = await client.send_message(channel, f)
											alertList[key] =  [i,msgs]
						msg1 = ""
						if val[2] == "alerts":
							try:
								msg1 = await client.get_message(channel,val[1])
								await client.edit_message(msg1,msg)
							except discord.NotFound:
								sql = "DELETE FROM alertmessages WHERE messageid=%s LIMIT 1"
								args = (val[1],)
								db.delete(sql, args)
							except discord.HTTPException:
								pass
						if val[2] == "poe":
							try:
								msg1 = await client.get_message(channel,val[1])
								if wfinfo[0][0]=="Night":
									await client.edit_message(msg1,"`PoE status: Night`")
									for i,j in tridolons.items():
										if key==i:
											if len(tempmsg)==0:
												tempmsg.append(await client.send_message(channel,j))
												tmplist.append(channel.server.id)
											else:	
												if key not in tmplist:
													tempmsg.append(await client.send_message(channel,j))
													tmplist.append(channel.server.id)
								else:
									await client.edit_message(msg1,"`PoE status: Day`")
							except discord.NotFound:
								sql = "DELETE FROM alertmessages WHERE messageid=%s AND channel_id=%s LIMIT 1"
								args = (val[1],val[0])
								db.delete(sql, args)
							except discord.HTTPException:
								pass
							if wfinfo[0][0]=="Day":
								for s in tempmsg:
									await client.delete_message(s)
								tempmsg.clear()
								tmplist.clear()
								tempmsg = []

		else:
			print("wtf")
		for j,k in alertList.items():
			if k[0].isExpired():
				keystodel.append(j)
				try:
					await client.delete_message(k[1])
				except discord.NotFound:
					pass
		for i in keystodel:
			try:
				del alertList[i]
			except:
				pass
		else:
			keystodel.clear()