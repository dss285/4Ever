from forever.dataClasses import node
import discord
import datetime
import operator
import time

# data = {"rewards", goal,count, faction}
# invasiondata = {start}
class InvasionObj:
    class InvasionOpp:
        def __init__(self, data, deforattack, fraction):
            self.rewards = data["rewards"]
            self.fraction = fraction
            self.faction = data["faction"].replace("FC_", "")
        def rewardReturn(self,):
            if self.rewards:
                return self.rewards["count"]+"x "+self.rewards["item"]
            else:
                return "N/A"

    def __init__(self, otherdata, attackerdata, defenderdata):
        deffra = str(round((otherdata["goal"]-otherdata["count"])/otherdata["goal"]*100,1))
        attackfra = str(round(otherdata["count"]/otherdata["goal"]*100,1))
        self.otherdata = otherdata

        self.attacker = InvasionObj.InvasionOpp(attackerdata, "Attacker", attackfra)
        self.defender = InvasionObj.InvasionOpp(defenderdata, "Defender", deffra)

        self.node = node.Node(otherdata["planet"], otherdata["node_name"])
    
    def returnInvStrings(self,):
        return {
            "rewards": self.attacker.rewardReturn()+" vs " + self.defender.rewardReturn(), 
            "location" : self.node.planet+", "+self.node.name, 
            "starttime" : self.otherdata["start"],
            "factions" : self.defender.faction+" vs "+self.attacker.faction,
            "fractions" : self.defender.fraction+"% vs "+self.attacker.fraction+"%"
        }

