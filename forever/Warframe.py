import discord
import asyncio
import time
import aiohttp
import re
import pathlib
import os
import json
from bs4 import BeautifulSoup
from datetime import datetime
from models.UpdatedMessage import UpdatedMessage
from models.EmbedTemplate import EmbedTemplate
from models.BotMention import BotMention
from forever import Utilities
class SolSystem():
	class SolPlanet:
		def __init__(self, id, name):
			self.id = id
			self.name = name
	class SolNode:
		def __init__(self, id, name, planet):
			self.id = id
			self.name = name
			self.planet = planet
class DropTables():
	def __init__(self) -> None:
		self.data = {}
		self.time_updated = 0
		self.interval = 86400
		self.session = None
	async def getData(self,):
		xx = time.time()
		if xx - self.time_updated > self.interval: #12h
			self.time_updated = time.time()
			if self.session:
				async with self.session.get("https://n8k6e2y6.ssl.hwcdn.net/repos/hnfvc0o3jnfvc873njb03enrf56.html") as r:
					if r.status==200:
						parsing = await r.text()
						reg = re.findall("<h3 id=\"(\w+)\">(.*?)<\/h3>\s*<table>([\s\S]*?)<\/table>", parsing, re.MULTILINE|re.DOTALL)
						for i in reg:
							parser = BeautifulSoup(i[2], 'html.parser')
							table_rows = parser.find_all('tr')
							self.data[i[0]] = {}
							self.data[i[0]]["title"] = i[1].replace(":", "")
							self.data[i[0]]["data"] = []
							tmp = {}
							if i[0] == "missionRewards" or i[0] == "keyRewards" or i[0] == "transientRewards":
								tmp_mission = None
								tmp_rotation = None
								for x in table_rows:
									text = x.get_text()
									if x.select('th') and "Rotation" not in text:
										tmp_mission = text
										tmp_rotation = None
										tmp[tmp_mission] = {}
									elif "Rotation" in text:
										tmp_rotation = text
										tmp[tmp_mission][tmp_rotation] = []
									else:
										if tmp_rotation:
											tmp[tmp_mission][tmp_rotation].append(text)
										elif "data" in tmp[tmp_mission]:
											tmp[tmp_mission]["data"].append(text)
										else:
											tmp[tmp_mission]["data"] = []
											tmp[tmp_mission]["data"].append(text)
								self.data[i[0]]["data"] = tmp
							elif i[0] == "relicRewards":
								relicname = None
								rarity = None
								for x in table_rows:
									text = x.get_text()
									if "Relic" in text:
										relic_match = re.match("((?:Axi|Neo|Meso|Lith|Requiem)\s\w{0,3}\d{0,2}\s?Relic)\s\((Radiant|Exceptional|Flawless|Intact)\)", text)
										if relic_match.group(1) in tmp:
											if relic_match.group(2) not in tmp[relic_match.group(1)]:
												tmp[relic_match.group(1)][relic_match.group(2)] = []
												rarity = relic_match.group(2)
										else:
											tmp[relic_match.group(1)] = {}
											tmp[relic_match.group(1)][relic_match.group(2)] = []
											rarity = relic_match.group(2)
											relicname = relic_match.group(1)
									else:
										tmp[relicname][rarity].append(text)
							elif i[0] == "sortieRewards":
								tmp = []
								for x in table_rows:
									text = x.get_text()
									if not x.select('th'):
										tmp.append(text)
							elif i[0] == "cetusRewards" or i[0] == "solarisRewards" or i[0] == "deimosRewards":
								tmp = {}
								bounty = None
								stage = None
								rotation = None
								for x in table_rows:
									text = x.get_text()
									if x.select('th'):
										if "Bounty" in text:
											bounty = text
											tmp[bounty] = {}
										elif "Rotation" in text:
											rotation = text
											tmp[bounty][rotation] = {}
										elif "Stage" in text:
											stage = text
											tmp[bounty][rotation][stage] = []
									else:
										tmp[bounty][rotation][stage].append(text)
							elif i[0] in set("modByAvatar", "blueprintByAvatar", "resourceByAvatar", "sigilByAvatar", "additionalItemByAvatar"):
								drop = None
								for x in table_rows:
									text = x.get_text()
									itemtitles = re.match(r"^([\s\S]+?)(?:Additional Item|Mod|Resource|Blueprint\/Item|Sigil) Drop Chance: (\d{0,3}\.\d{0,3})\%$", text)
									if itemtitles:
										drop = itemtitles.group(1)
										tmp[drop] = {}
										tmp[drop]["chance"] = itemtitles.group(2)
										tmp[drop]["data"] = []
									else:
										tmp[drop]["data"].append(text)
							elif i[0] in set("modByDrop", "blueprintByDrop", "resourceByDrop"):
								drop = None
								for x in table_rows:
									text = x.get_text()
									if x.select('th'):
										if "Source" not in text:
											drop = text
											tmp[drop] = []
									else:
										tmp[drop].append(text)
							self.data[i[0]]["data"] = tmp
	def searchKey(self, key, searched_value):
		vals = []
		for i in self.data[key]["data"]:
			if i.lower().startswith(searched_value.lower()):
				vals.append(i)
		return vals
	def relicSearch(self, searched_value):
		vals = self.searchKey("relicRewards", searched_value)
		if len(vals) == 1:
			em = EmbedTemplate(title=self.data["relicRewards"]["title"], description=vals[0])
			for i, j in self.data["relicRewards"]["data"][vals[0]].items():
				em.add_field(name=i, value="\n".join(j))
			return em
		else:
			return EmbedTemplate(title=self.data["relicRewards"]["title"], description="\n".join(vals))
class CetusStatus:
	def __init__(self, expiry):
		self.expiry = expiry
		self.start = self.expiry-150*60
	def isNight(self,):
		if self.minutes_left() <= 50:
			return True
		else:
			return False
	def seconds_left(self):
		return self.expiry-time.time()
	def minutes_left(self,):
		return self.seconds_left()//60
	def __str__(self,):
		return "Night" if self.isNight() else "Day"
class CetusMessage(UpdatedMessage):
	def __init__(self, message, mention, client):
		self.mention = mention
		self.notify_message = None
		self.lock = False
		self.client = client
		super().__init__(message, "poe")
	async def refresh(self, cetus):
		em = EmbedTemplate(title="Plains of Eidolon", timestamp=datetime.utcnow())
		em.add_field(name="Status", value=str(cetus))
		em.add_field(name="Time until new rotation", value=f"{cetus.minutes_left() if cetus else 0.00:.0f} min")
		await self.message.edit(embed=em)
		if not self.lock:
			if cetus.isNight() and self.mention:
				self.lock = True
				self.notify_message = await self.message.channel.send(f"{self.mention.name} - {self.mention.role.mention}")
				self.client.loop.call_later(cetus.seconds_left()+60, self.callback)
	def callback(self,):
		self.client.loop.create_task(self.remove_message())
		self.lock = False
	async def remove_message(self,):
		await self.notify_message.delete()
		self.notify_message = None
class FissureItem:
	def __init__(self, oid, start_time, expiry_time, mission_type, node, era):
		self.start_time = start_time
		self.expiry_time = expiry_time
		self.mission_type = mission_type
		self.node = node
		self.era = era
	def expiresIn(self,):
		return self.expiry_time-time.time()
	def __str__(self,):
		if type(self.node) == str:
			tmp = f"{self.node.title()}, {self.node.title()}"
			return f"{tmp}\n{(f'Expires on {Utilities.ts2string(self.expiry_time)}')}\nExpires in {self.expiresIn()//60:.0f} min"
		tmp = self.node.planet.name.title()+", "+self.node.name.title()
		return f"{tmp}\n{(f'Expires on {Utilities.ts2string(self.expiry_time)}')}\nExpires in {self.expiresIn()//60:.0f} min"
class FissureMessage(UpdatedMessage):
	def __init__(self, message, mentions):
		super().__init__(message, "fissures")
		self.mentions = mentions
	async def refresh(self, fissures):
		em = EmbedTemplate(title="Fissures", timestamp=datetime.utcnow())
		for i in fissures:
			em.add_field(name=f"{i.era} {i.mission_type}", value=str(i))
		await self.message.edit(embed=em)
class InvasionItem:
	def __init__(self, attacker, defender, node, starttime, status):
		self.attacker = attacker
		self.defender = defender
		self.start_time = starttime
		self.node = node
		self.status = status
class InvasionOpp:
	#0 DEFENDING
	#1 ATTACKING
	def __init__(self, faction, rewards):
		self.faction = faction
		self.rewards = rewards
class InvasionMessage(UpdatedMessage):
	def __init__(self, message, mentions):
		super().__init__(message, "invasions")
		self.mentions = mentions
	async def refresh(self, invasions):
		em = EmbedTemplate(title="Invasions", timestamp=datetime.utcnow())
		for i in invasions:
			vals = []
			if type(i.node) == str:
				vals.append(f"{i.node.title()}, {i.node.title()}")
			else:
				vals.append(f"{i.node.planet.name.title()}, {i.node.name.title()}")
			vals.append(i.start_time)
			vals.append(f"{i.defender.faction} vs {i.attacker.faction}"),
			vals.append(i.status)

			em.add_field(
			name=f"{i.defender.rewards} vs {i.attacker.rewards}", 
			value=f"{vals[0]}\n{vals[1]}\n{vals[2]}\n{vals[3]}\n\u200b")
		await self.message.edit(embed=em)
class NightwaveItem:
	def __init__(self, start_time, expiry_time, name, daily=False):
		self.start_time = start_time
		self.expiry_time = expiry_time
		self.name = name
		self.daily = daily
class NightwaveMessage(UpdatedMessage):
	def __init__(self, message):
		super().__init__(message, "nightwave")

	async def refresh(self, nightwave_data):
		em = EmbedTemplate(title="Nightwave", timestamp=datetime.utcnow())
		for i in nightwave_data:
			em.add_field(name=i.name, value=(Utilities.ts2string(i.start_time+(60*120))+"\n\n"))
		
		await self.message.edit(embed=em)
class Sorties:
	class SortieItem:
		def __init__(self, start_time, expiry_time, missions):
			self.start_time = start_time
			self.expiry_time = expiry_time
			self.missions = missions
	class SortieMission:
		def __init__(self, missionType, node, modifier):
			self.mission_type = missionType
			self.node = node
			self.modifier = modifier
		def __str__(self,):
			if type(self.node) == str:
				return f"{self.mission_type}\n{self.node}\n{self.modifier}"
			return f"{self.mission_type}\n{(f'{self.node.name.title()}, {self.node.planet.name.title()}')}\n{self.modifier}"
class SortieMessage(UpdatedMessage):
	def __init__(self, message):
		super().__init__(message, "sorties")
	async def refresh(self, sortie):
		em = EmbedTemplate(title="Sorties", timestamp=datetime.utcnow())
		count = 1
		for i in sortie.missions:
			em.add_field(name=f"Mission {count}", value=str(i))
			count+=1
		await self.message.edit(embed=em)
class Worldstate():
	def __init__(self,):
		self.runtime = {}
		self.fissure_eras = {
			"VoidT1" : ["Lith",     1],
			"VoidT2" : ["Meso",     2],
			"VoidT3" : ["Neo",      3],
			"VoidT4" : ["Axi",      4],
			"VoidT5" : ["Requiem",  5]
		}
		self.session = None
		self.initRuntime()
	def initRuntime(self,):
		self.runtime.clear()
		self.runtime["invasions"] = []
		self.runtime["nightwave"] = []
		self.runtime["fissures"] = []
		self.runtime["sorties"] = None
		self.runtime["poe"] = None
	def getInvasions(self, parsing, data_runtime):
		for invasion in parsing["Invasions"]:
			if not invasion["Completed"]:
				start_time = int(invasion["Activation"]["$date"]["$numberLong"])//1000
				node = next((x for x in data_runtime["warframe"]["translate"]["solsystem"]["nodes"] if x.id == invasion["Node"]), invasion["Node"])
				attack_reward = "N/A"
				defender_reward = "N/A"
				reward_item = invasion["DefenderReward"]["countedItems"][0]["ItemType"]
				translate = data_runtime["warframe"]["translate"]["items"]
				defender_reward = f"{invasion['DefenderReward']['countedItems'][0]['ItemCount']}x {translate[reward_item] if  reward_item in translate else reward_item}"
				if invasion["AttackerReward"]:
					reward_item = invasion["AttackerReward"]["countedItems"][0]["ItemType"]
					attack_reward = f"{invasion['AttackerReward']['countedItems'][0]['ItemCount']}x { translate[reward_item] if  reward_item in translate else reward_item}"
				attack_faction = invasion["AttackerMissionInfo"]["faction"].strip("FC_")
				defender_faction = invasion["DefenderMissionInfo"]["faction"].strip("FC_")
				goal = invasion["Goal"]*2
				current = invasion["Count"]+invasion["Goal"]
				fraction_attacker = round(current/goal*100,1)
				fraction_defender = round((goal-current)/goal*100,1)
				attacker = InvasionOpp(attack_faction, attack_reward)
				defender = InvasionOpp(defender_faction, defender_reward)
				self.runtime["invasions"].append(InvasionItem(attacker, defender, node, Utilities.ts2string(start_time), f"{fraction_defender}% vs {fraction_attacker}%"))
	def getNightwave(self, parsing, data_runtime):
		translate = data_runtime["warframe"]["translate"]
		for nightwave in parsing["SeasonInfo"]["ActiveChallenges"]:
			challenge = translate["nightwave"][nightwave["Challenge"]] if nightwave["Challenge"] in translate["nightwave"] else nightwave["Challenge"]
			daily = nightwave["Daily"] if "Daily" in nightwave else False
			start_time = int(nightwave["Activation"]["$date"]["$numberLong"])//1000
			expiry_time = int(nightwave["Expiry"]["$date"]["$numberLong"])//1000
			self.runtime["nightwave"].append(NightwaveItem(start_time, expiry_time, challenge, daily))
	def getFissure(self, parsing, data_runtime):
		translate = data_runtime["warframe"]["translate"]
		for fissure in sorted(parsing["ActiveMissions"], key=lambda item: self.fissure_eras[item["Modifier"]][1]):
			oid = fissure["_id"]["$oid"]
			start_time = int(fissure["Activation"]["$date"]["$numberLong"])//1000
			expiry_time = int(fissure["Expiry"]["$date"]["$numberLong"])//1000 
			mission_type = translate["missions"][fissure["MissionType"]].title() if fissure["MissionType"] in translate["missions"] else fissure["MissionType"]
			node = next((x for x in translate["solsystem"]["nodes"] if x.id == fissure["Node"]), fissure["Node"])
			era = self.fissure_eras[fissure["Modifier"]][0]
			self.runtime["fissures"].append(FissureItem(oid, start_time, expiry_time, mission_type, node, era))
	def getSorties(self, parsing, data_runtime):
		if parsing["Sorties"]:
			start_time = int(parsing["Sorties"][0]["Activation"]["$date"]["$numberLong"])//1000
			expiry_time = int(parsing["Sorties"][0]["Expiry"]["$date"]["$numberLong"])//1000
			missionsParse = parsing["Sorties"][0]["Variants"]
			missions = []
			translate = data_runtime["warframe"]["translate"]
			for i in missionsParse:
				mission_type = translate["missions"][i["missionType"]].title() if i["missionType"] in translate["missions"] else i["missionType"].title()
				node = next((x for x in translate["solsystem"]["nodes"] if x.id == i["node"]), i["node"])
				modifier = translate["sorties"][i["modifierType"]].title() if i["modifierType"] in translate["sorties"] else i["modifierType"]
				missions.append(Sorties.SortieMission(mission_type, node, modifier))
			self.runtime["sorties"] = Sorties.SortieItem(start_time, expiry_time, missions)
	def getCetus(self, parsing, data_runtime):
		expiry_time = next(((int(x["Expiry"]["$date"]["$numberLong"])//1000) for x in parsing["SyndicateMissions"] if x["Tag"] == "CetusSyndicate"), None)
		if expiry_time:
			self.runtime["poe"] = CetusStatus(expiry_time)
	async def get_data(self, data_runtime):
		self.initRuntime()
		if self.session:
			async with self.session.get("http://content.warframe.com/dynamic/worldState.php") as r:
				if r.status==200:
					parsing = await r.text()
					parsing = json.loads(parsing)

					if "Invasions" in parsing:
						self.getInvasions(parsing, data_runtime)

					if "SeasonInfo" in parsing and parsing["SeasonInfo"]:
						self.getNightwave(parsing, data_runtime)

					if "ActiveMissions" in parsing:
						self.getFissure(parsing, data_runtime)

					if "Sorties" in parsing:
						self.getSorties(parsing, data_runtime)

					if "SyndicateMissions" in parsing:
						self.getCetus(parsing, data_runtime)
