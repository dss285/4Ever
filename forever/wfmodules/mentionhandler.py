import discord
import asyncio
import time
class MentionHandler():
	def __init__(self,):
		self.mentions = {}
	def addMention(self,server, m_type , message, expiry, oid):
		if server not in self.mentions:
			self.mentions[server] = {
					"fissure" : {},
					"tridolon" : {},
					"invasions" : {}
			}
		self.mentions[server][m_type][oid] = {"special" : False, "message" : message, "expiry" : expiry}

	def addSpecialMention(self, server, m_type, message, oid):
		if server not in self.mentions:
			self.mentions[server] = {
					"fissure" : {},
					"tridolon" : {},
					"invasions" : {}
			}
		self.mentions[server][m_type][oid] = {"special" : True, "message" : message}
	def itemIn(self,server, oid, m_type):
		if server in self.mentions:
			for i in self.mentions[server][m_type]:
				if i == oid:
					return True
			return False
		else:
			return False
	async def removeMention(self, key, m_type, oid):
		count = 0
		for i in self.mentions[key][m_type]:
			if oid == i:
				await self.mentions[key][m_type][i]["message"].delete()
				break
			count += 1
		del self.mentions[key][m_type][count]
	async def checkAllMentions(self,):
		tmp = []
		for i in self.mentions:
			mtype = self.mentions[i]
			for mtypekey, mtypevalue in mtype.items():
				#keys : fissure, tridolon
				#vals : lists with dictionarys
				for j,k in mtypevalue.items():
					#every list item processed, as they are dictionaries
					#self.mentions[server][m_type].append({"special" : False, "message" : message, "expiry" : expiry, "oid" : oid})
					if not k["special"]:
						if k["expiry"] <= time.time():
							await k["message"].delete()
							#server, key, id
							tmp.append([i,mtypekey,j])
		for i in tmp:
			del self.mentions[i[0]][i[1]][i[2]]
		tmp = None
