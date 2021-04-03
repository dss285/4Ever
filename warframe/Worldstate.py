import asyncio
import aiohttp
import discord
import json
from forever.Database import Database
from forever import Utilities
from warframe.NightwaveItem import NightwaveItem
from warframe.FissureItem import FissureItem
from warframe.CetusStatus import CetusStatus
import warframe.InvasionItem as InvItem
import warframe.Sorties as Sorties
class Worldstate():
    def __init__(self):
        self.runtime = {}
        self.fissure_eras = {
			"VoidT1" : ["Lith",     1],
			"VoidT2" : ["Meso",     2],
			"VoidT3" : ["Neo",      3],
			"VoidT4" : ["Axi",      4],
			"VoidT5" : ["Requiem",  5]
		}
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
                defender_reward = "{}x {}".format(
                    invasion["DefenderReward"]["countedItems"][0]["ItemCount"],
                    translate[reward_item] if  reward_item in translate else reward_item
                )
                if invasion["AttackerReward"]:
                    reward_item = invasion["AttackerReward"]["countedItems"][0]["ItemType"]
                    attack_reward = "{}x {}".format(
                        invasion["AttackerReward"]["countedItems"][0]["ItemCount"],
                        translate[reward_item] if  reward_item in translate else reward_item
                    )
                attack_faction = invasion["AttackerMissionInfo"]["faction"].strip("FC_")
                defender_faction = invasion["DefenderMissionInfo"]["faction"].strip("FC_")
                goal = invasion["Goal"]*2
                current = invasion["Count"]+invasion["Goal"]
                fraction_attacker = round(current/goal*100,1)
                fraction_defender = round((goal-current)/goal*100,1)
                attacker = InvItem.InvasionOpp(attack_faction, attack_reward)
                defender = InvItem.InvasionOpp(defender_faction, defender_reward)
                self.runtime["invasions"].append(InvItem.InvasionItem(attacker, defender, node, Utilities.ts2string(start_time), "{}% vs {}%".format(fraction_defender, fraction_attacker)))
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
    async def getData(self, data_runtime):
        self.initRuntime()
        async with aiohttp.ClientSession() as sess:
            async with sess.get("http://content.warframe.com/dynamic/worldState.php") as r:
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
