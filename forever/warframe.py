import json
import re
import time
import datetime
import os
import sys
import pytz
import re
import discord
import aiohttp
import traceback
from bs4 import BeautifulSoup
from forever.dataClasses import invasion
from forever.dataClasses import nightwave
from forever.dataClasses import fissure
from forever.dataClasses import node
from forever import dataClasses
from forever.wfmodules import mentionhandler
import asyncio
class Warframe:
	def __init__(self, db, helper):
		self.db = db
		self.helper = helper
		self.items = db["items"]
		self.sortiemodifiers = db["sorties"]
		self.nightwaveChallenges = db["nightwave"]
		self.builds = db["builds"]
		self.missionTypes = db["missions"]

		self.locations = None
		self.returnNodes()
	def returnNodes(self, ):
		tmp = self.db["solsystem"]
		tmp1 = tmp["nodes"]
		tmp2 = tmp["planets"]
		planets = {}
		for i in tmp2:
			planets[str(i["planet_id"])] = i["name"]
		nodes = {}
		for i in tmp1:
			nodes[i["node_id"]] = {"planet" : i["planet_id"], "name" : i["name"]}
		self.locations = {"planets" : planets, "nodes" : nodes}
	def updatedb(self, db):
		self.db = db
		self.items = db["items"]
		self.sortiemodifiers = db["sorties"]
		self.nightwaveChallenges = db["nightwave"]
		self.builds = db["builds"]
		self.missionTypes = db["missions"]
		self.returnNodes()

	async def sendBuildItems(self, message, key, command):
		fields = ["warframe","primary", "secondary", "melee", "companion"]
		reg = re.match(key+""+command+"\s(.*)\s(.*)", message.content)
		if reg:
			if reg.group(1).lower() in fields:
				if reg.group(2).lower() in ["list", "all"]:
					em = discord.Embed(title=reg.group(1).title(), description="\n".join(self.db["images"]["builds"][reg.group(1).lower()]))
					await message.channel.send(embed=em)
				elif reg.group(2).lower() in self.db["images"]["builds"][reg.group(1).lower()]:
					em = discord.Embed(title=reg.group(1).title(), description="[{link}](".format(link=reg.group(2).title())+self.db["images"]["builds"][reg.group(1).lower()][reg.group(2).lower()]+")")
					await message.channel.send(embed=em)
		else:
			em = discord.Embed(title="Build Types", description="Use: {key}{command} ({l_all}) (options below)\n".format(key=key,command=command,l_all=" | ".join(["list", "all"]+fields))+"\n".join(fields))
			await message.channel.send(embed=em)
	
	async def sendBuildBundle(self, message, key, command):
		reg = re.match(key+""+command+"\s(.*)", message.content)
		if reg:
			if reg.group(1).lower() in ["list", "all"]:
				content = ""
				for i in self.builds.keys():
					content = content+i.title()+"\n"
				msg = discord.Embed(title="Build List",description=content,colour=0x8A00E0)
				await message.channel.send(embed=msg)
			elif reg.group(1).lower() in self.builds.keys():
				build = self.builds[reg.group(1).lower()]
				em = discord.Embed(title=reg.group(1).title(), description=build["description"])
				em.add_field(name="Warframe",value="[{link}](".format(link=reg.group(1).title())+self.db["images"]["builds"]["warframe"][reg.group(1).lower()]+")", inline=False)
				fields = ["primary", "secondary", "melee", "companion"]
				for i in fields:
					if i in self.db["images"]["builds"][i]:
						em.add_field(name=i.title(),value="[{link}](".format(link=build[i].title())+self.db["images"]["builds"][i][build[i]]+")", inline=False)

				await message.channel.send(embed=em)
		else:
			em = discord.Embed(title="Loadout Build", description="Use {key}{command} ({l_all})".format(key=key,command=command, l_all="|".join(["list", "all"])))
			await message.channel.send(embed=em)

	async def getInfo(self,db):
		try:
			self.updatedb(db)
			async with aiohttp.ClientSession() as sess:
				async with sess.get("http://content.warframe.com/dynamic/worldState.php") as r:
					if r.status==200:
						alertList = []
						cetusStatus = ""
						try:
							parsing = await r.text()
						except Exception as e:
							print("warfame.py l101:"+e)
						parsing = json.loads(parsing)
						fissureslist = []
						nightwave_parse = []
						sorties = []
						invasions = []
						fo = open("worldstate","w+")
						fo.write(json.dumps(parsing, sort_keys=True, indent=2))
						fo.close()
						if "ActiveMissions" in parsing:
							for i in parsing["ActiveMissions"]:
								oid = i["_id"]["$oid"]
								expiry = int(i["Expiry"]["$date"]["$numberLong"])/1000
								start = int(i["Activation"]["$date"]["$numberLong"])/1000
								missiontype = self.missionTypes[i["MissionType"]].title()
								nodedata = self.locations["nodes"][i["Node"]] if i["Node"] in self.locations["nodes"] else i["Node"]
								planet = self.locations["planets"][str(nodedata["planet"])].title() if i["Node"] in self.locations["nodes"] else i["Node"]
								nodename = nodedata["name"].title() if i["Node"] in self.locations["nodes"] else i["Node"]
								#def __init__(self, planet, name):
								nodeobj = node.Node(planet, nodename)
								#def __init__(self, mission_type, node, tier, expiry, start):
								fissureslist.append(fissure.FissureObj(missiontype, nodeobj, i["Modifier"], expiry, start, oid))
						if "Sorties" in parsing:
							if parsing["Sorties"]:
								sorties = parsing["Sorties"][0]
							else:
								sorties = None
						if "Invasions" in parsing:
							if parsing["Invasions"]:
								for i in parsing["Invasions"]:
									if not i["Completed"]:
										nodedata = self.locations["nodes"][i["Node"]] if i["Node"] in self.locations["nodes"] else i["Node"]
										planet = self.locations["planets"][str(nodedata["planet"])].title() if i["Node"] in self.locations["nodes"] else i["Node"]


										attackerdata = {}
										if i["AttackerReward"]:
											attackerdata["rewards"] = {
														"count" : str(i["AttackerReward"]["countedItems"][0]["ItemCount"]),
														"item" : self.items[i["AttackerReward"]["countedItems"][0]["ItemType"]]
													}
										else:
											attackerdata["rewards"] = None

										attackerdata["faction"] = i["AttackerMissionInfo"]["faction"]
										defenderdata = {}
										defenderdata["rewards"] = { "count" : str(i["DefenderReward"]["countedItems"][0]["ItemCount"]), "item" : self.items[i["DefenderReward"]["countedItems"][0]["ItemType"]]}
										defenderdata["faction"] = i["DefenderMissionInfo"]["faction"]

										otherdata={
										"start" : self.helper.timestamp2string(int(i["Activation"]["$date"]["$numberLong"])/1000,'%d.%m.%Y %H:%M:%S | %Z%z'), 
										"oid" : i["_id"]["$oid"], 
										"planet" : planet, 
										"node_name": nodedata["name"].title() if i["Node"] in self.locations["nodes"] else i["Node"],
										"goal" : i["Goal"]*2,
										"count" : i["Count"]+i["Goal"]}
										invasions.append(invasion.InvasionObj(otherdata, attackerdata, defenderdata))
							else:
								invasions = None
						if "SeasonInfo" in parsing and parsing["SeasonInfo"]:
							nightwaveL = parsing["SeasonInfo"]["ActiveChallenges"]
							nightwave_parse = []
							for i in nightwaveL:
								challenge = i["Challenge"]
								start = int(i["Activation"]["$date"]["$numberLong"])/1000
								expiry = int(i["Expiry"]["$date"]["$numberLong"])/1000
								if "Daily" in i.keys():
									daily = i["Daily"]
								else:
									daily = False
								nightwave_parse.append(nightwave.Nightwave(challenge,start,expiry,daily))
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
				return {"poe":[cetusStatus,expiryTime],"nightwave":nightwave_parse,
				"sorties":sorties, "invasions" : invasions, "fissures":fissureslist}
		except Exception as e:
			print(e)
			traceback.print_exc()
			return None


	async def fissures(self, client, wfinfo, handler, helper, key, val):
		channel = client.get_channel(val[0])
		msg1 = await channel.fetch_message(val[1])
		fissures = fissure.Fissures(wfinfo["fissures"])
		if msg1 != None:
			msg = fissures.message(helper)
			msg.set_thumbnail(url=self.db["images"]["messages"]["fissures"])
			for i in wfinfo["fissures"]:
				role_mentions = self.db["servers"][key]["notifications"]
				if not handler.itemIn(key, i.oid, "fissure"):
					mentioncheck = i.tier.lower()+""+i.mission_type.lower()
					if mentioncheck in role_mentions:
						#def addMention(self,server, m_type , message, expiry, oid):
						handler.addMention(key, "fissure", await channel.send(role_mentions[mentioncheck]),i.expiry, i.oid)
						
			await msg1.edit(embed=msg)
	async def nightwave(self, client, wfinfo, key, val):
		msg1 = None
		msg1 = await client.get_channel(int(val[0])).fetch_message(int(val[1]))
		if msg1 != None:
			msg = discord.Embed(title="Nightwave Challenges",colour=0x8A00E0,timestamp=datetime.datetime.utcnow())
			msg.set_thumbnail(url=self.db["images"]["messages"]["nightwave"])
			for i in wfinfo["nightwave"]:
				challenge = ""
				if i.challenge not in self.nightwaveChallenges.keys():
					challenge = i.challenge
					fh = open('forever/missing.txt','r+')
					if "\""+i.challenge+"\":\"\",\n" not in fh.readlines():
						fh.write("\""+i.challenge+"\":\"\",\n")
					fh.close()
				else:
					challenge = self.nightwaveChallenges[i.challenge]
				msg.add_field(name=challenge,value=("Expires on "+
					time.strftime("%d.%m.%y %H:%M",time.gmtime(i.expiry+(60*120)))+"\n\n"), inline=True)
			await msg1.edit(embed=msg)
	async def sorties(self, client, wfinfo,  helper, key, val):
		channel = client.get_channel(int(val[0]))
		msg1 = await channel.fetch_message(int(val[1]))
		if msg1 != None:
			if wfinfo["sorties"]:
				expiredtime = helper.timestamp2string(int(wfinfo["sorties"]["Expiry"]["$date"]["$numberLong"])/1000,'%d.%m.%Y %H:%M:%S | %Z%z')
				msg = discord.Embed(colour=0x8A00E0,timestamp=datetime.datetime.utcnow(), title="Sorties", 
						description="Expires on **{expiry}**".format(expiry=expiredtime))
				msg.set_thumbnail(url=self.db["images"]["messages"]["sorties"])
				missions = wfinfo["sorties"]["Variants"]
				count=1
				#nodes[i["node_id"]] = {"planet" : i["planet_id"], "name" : i["name"]}
				# self.locations = {
					# "planets" : planets,
					# "nodes" : nodes
				# }
				for i in missions:
					tmp = self.locations["nodes"][i["node"]] if i["node"] in self.locations["nodes"] else i["node"]
					planet = self.locations["planets"][str(tmp["planet"])].title() if tmp != i["node"] else i["node"]
					nodename = tmp["name"].title() if tmp != i["node"] else i["node"]
					msg.add_field(name="Mission {number}".format(number=count), 
					value="Type: {missiontype}\nModifier: {modifier}\nLocation: {location}".format(missiontype=self.missionTypes[i["missionType"]].title(), 
						modifier=self.sortiemodifiers[i["modifierType"]].title(),location=planet+" "+nodename),inline=False)
					count +=1
				await msg1.edit(embed=msg)
	async def invasions(self, client, wfinfo,  handler, helper, key, val):
		tmp = []
		channel = client.get_channel(int(val[0]))
		msg1 = await channel.fetch_message(int(val[1]))
		msg = discord.Embed(colour=0x8A00E0,timestamp=datetime.datetime.utcnow(), title="Invasions")
		if msg1 != None:
			msg = discord.Embed(colour=0x8A00E0,timestamp=datetime.datetime.utcnow(), title="Invasions")
			msg.set_thumbnail(url=self.db["images"]["messages"]["invasions"])
			for i in wfinfo["invasions"]:
				returnInvStrings = i.returnInvStrings()
				valuetomsg = "{location}\n{starttime}\n{factions}\n{fractions}\n\u200b".format(location=returnInvStrings["location"], starttime=returnInvStrings["starttime"], factions=returnInvStrings["factions"], fractions=returnInvStrings["fractions"])
				msg.add_field(name=returnInvStrings["rewards"], value=valuetomsg)
					#     "_id": {"$oid": "5d3e3cdd7ca2bf5f9f071e09"}
				role_mentions = self.db["servers"][key]["notifications"]
				oid = i.otherdata["oid"]
				msgt = ""
				if not handler.itemIn(key, oid, "invasions"):
					for j in role_mentions:
						if i.attacker.rewards:
							
							if j.lower() in i.defender.rewards["item"].lower():
								msgt = msgt+ role_mentions[j]+"\n"
							elif j.lower() in i.attacker.rewards["item"].lower():
								msgt = msgt+ role_mentions[j]+"\n"
					if msgt:
						handler.addSpecialMention(key, "invasions", await channel.send(msgt), oid)	
						tmp.append(oid)

			await msg1.edit(embed=msg)
		if tmp:
			if key in handler.mentions:
				servermentions = handler.mentions[key]
				if servermentions["invasions"]:
					for i in servermentions["invasions"]:
						if i not in tmp:
							try:
								await handler.removeMention(key, "invasions", i)
							except Exception as e:
								print("warframe.py l289:"+e)
								pass	
	async def plains(self, client, wfinfo, handler, key, val, mention):
		channel = client.get_channel(int(val[0]))
		msg1 = await channel.fetch_message(int(val[1]))
		if msg1 != None:
			minutes = int((wfinfo["poe"][1]-time.time())/60)
			msg = discord.Embed(colour=0x8A00E0,timestamp=datetime.datetime.utcnow())
			msg.set_thumbnail(url=self.db["images"]["messages"]["plains"])
			msg.add_field(name="PoE Status",value=wfinfo["poe"][0])
			msg.add_field(name="Time until Rotation",value=str(minutes)+"m to ↻")
			await msg1.edit(embed=msg)
			if minutes < 53:
				if mention:
					if not handler.itemIn(key, wfinfo["poe"][1], "tridolon"):
						handler.addMention(key,"tridolon", await channel.send(mention), 
							wfinfo["poe"][1], wfinfo["poe"][1])