from forever.dataClasses import node
import discord
import datetime
import operator
import time
class FissureObj():
	def __init__(self, mission_type, nodeobj, tier, expiry, start, oid):
		
		types = {
			"VoidT1" : "Lith",
			"VoidT2" : "Meso",
			"VoidT3" : "Neo",
			"VoidT4" : "Axi",
			"VoidT5" : "Requiem"
		}
		typesn = {
			"VoidT1" : 1,
			"VoidT2" : 2,
			"VoidT3" : 3,
			"VoidT4" : 4,
			"VoidT5" : 5
		}
		
		self.mission_type = mission_type
		self.nodeobj = nodeobj
		self.tiern = typesn[tier]
		self.tier = types[tier]
		self.expiry = expiry
		self.start = start
		self.oid = oid
class Fissures():
	def __init__(self, fissures):
		self.fissures = fissures
	def message(self,helper):
		msg = discord.Embed(title="Fissures",colour=0x8A00E0,timestamp=datetime.datetime.utcnow())
		for i in sorted(self.fissures, key=operator.attrgetter('tiern')):
			expiry = i.expiry
			start = i.start
			expiryString = helper.timestamp2string(expiry, '%d.%m.%Y %H:%M:%S | %Z%z')
			missiontype = i.mission_type
			planet = i.nodeobj.planet
			nodename = i.nodeobj.name
			expiresin = round((expiry-time.time())//60)
			msg.add_field(name="{era} {missiontype}".format(era=i.tier, missiontype=missiontype), 
				value="{planet}, {node}\nExpires on {expiry}\nExpires in {minutes}m\n\u200b".format(planet=planet, node=nodename, expiry=expiryString, minutes=expiresin))
		return msg