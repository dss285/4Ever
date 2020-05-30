import re
import json
import discord
class Database:
	def __init__(self,):
		self.script_dir = "/home/dss/data/"
		self.keywords = ["tridolon"]
		self.updatedmessages = ["nightwave", "poe", "sorties", "invasions"]
		self.jsonDict = {}
		self.loadData()

	def getNightwave(self,):
		if "nightwave" in self.jsonDict:
			return self.jsonDict["nightwave"]
		else:
			return False
#edit database
	##work with dicts
	def modifySolSystem(self, action, i_id, data):
		# "solsystem": {
    	# 	"nodes": [
    	# 	  {
    	# 	    "name": "neruda",
    	# 	    "node_id": "SolNode221",
    	# 	    "planet_id": 0
    	# 	  },
		# 	"planets": [
      	# 	{
      	# 	  "name": "Mercury",
      	# 	  "planet_id": 0
      	# 	},

		#data has key which, has data if modifies planet or node
		which = data["which"]
		everythingok = False
		if action == "add":
			self.jsonDict["solsystem"][which+"s"].append(data["vars"])
			everythingok = True
		elif action == "edit":
			if i_id:
				self.jsonDict["solsystem"][which+"s"][i_id] = data["vars"]
				everythingok = True
		elif action == "remove":
			if i_id:
				del self.jsonDict["solsystem"][which+"s"][i_id]
				everythingok = True

		self.saveData()
		return everythingok
	def modifyBuilds(self, name, action, b_vars=None):
		# {
 		#  "builds": {
    	# 	"oberon tridolon": {
     	# 		"companion": "adarza",
    	# 		"description": "3",
    	# 		"melee": "sarpa",
    	# 		"primary": "lanka",
    	# 		"secondary": "catchmoon"
		everythingok = False
		if action == "add":
			if name in self.jsonDict["builds"]:
				name = name+"1"
			self.jsonDict["builds"][name] = b_vars
			everythingok = True
		elif action == "edit":
			if name in self.jsonDict["builds"]:
				tmp = self.jsonDict["builds"][name]
				for x, y in b_vars.items():
					if y != None or "null" or "None" or "0":
						tmp[x] = y
				self.jsonDict["builds"][name] = tmp
				everythingok = True
		elif action == "remove":
			if name in self.jsonDict["builds"]:
				del self.jsonDict["builds"][name]
				everythingok = True
		self.saveData()
		return everythingok
	def modifyImages(self, subcategory, action, i_id=None, link=None):
		everythingok = False
		if action == "add":
			self.jsonDict["images"][subcategory].append(link)
			everythingok = True
		elif action == "remove":
			del self.jsonDict["images"][subcategory][i_id]
			everythingok = True
		self.saveData()
		return everythingok
	def modifyBuildImages(self, build, name, action, link=None):
		#"images": {
    		#"builds": {
      			#"companion": {
        			#"adarza": "https://cdn.discordapp.com/attachments/610791252320845825/610791474799575068/Adarza.jpg"
		everythingok = False
		if action == "add" or action =="edit":
			if name in self.jsonDict["images"]["builds"][build] or action=="add":
				self.jsondict["images"]["builds"][build][name] = link
				everythingok = True
		elif action =="remove":
			if name in self.jsonDict["images"]["builds"][build]:
				del self.jsondict["images"]["builds"][build][name]
				everythingok = True
		self.saveData()
		return everythingok
	def modifyDicts(self, action, subcategory, i_id, name=None):
		#"items": {
    		#"/Lotus/StoreItems/Powersuits/Harlequin/LightAugmentCard": "Total Eclipse",
		everythingok = False
		if action == "add" or action == "edit" and name != None:
			self.jsonDict[subcategory][i_id] = name
			everythingok = True
		elif action == "remove":
			if i_id in self.jsonDict[subcategory]:
				del self.jsonDict[subcategory][i_id]
				everythingok = True
		self.saveData()
		return everythingok
	



#binds
	def bindJSON(self,keyword,roleid,serverid):
		everythingok = False
		serverid = str(serverid)
		if keyword.lower() in self.keywords:
			if serverid in self.jsonDict["servers"]:
				if keyword in self.jsonDict["servers"][serverid]["notifications"].keys():
					del self.jsonDict["servers"][serverid]["notifications"][keyword.lower()]
				self.jsonDict["servers"][serverid]["notifications"][keyword.lower()] = roleid
				self.saveData()
				everythingok = True
			else:
				self.newServer(serverid)
				self.bindJSON(keyword, roleid, serverid)
				everythingok = True
		return everythingok
	def removeBindJSON(self,keyword, serverid):
		serverid = str(serverid)
		everythingok = False
		if keyword in self.keywords:
			if serverid in self.jsonDict["servers"].keys():
				if keyword in self.jsonDict["servers"][serverid]["notifications"].keys():
					del self.jsonDict["servers"][serverid]["notifications"][keyword]
					everythingok = True
		return everythingok
	def bindList(self,):
		em = discord.Embed(title="Bind List", description="\n".join(self.keywords))
		return em
#roles
	def addRole(self,serverid,roleid):
		serverid = str(serverid)
		self.jsonDict["servers"][serverid]["joinable_roles"].append(str(roleid))
		self.saveData()
		return True
	def removeRole(self,serverid,roleid):
		serverid = str(serverid)
		self.jsonDict["servers"][serverid]["joinable_roles"].remove(str(roleid))
		self.saveData()
		return True
#messages
	def addNotificationMessage(self,serverid, stored, msgtype):
		everythingok = False
		serverid = str(serverid)
		if serverid in self.jsonDict["servers"].keys():
			if msgtype in self.jsonDict["servers"][serverid]["updated"].keys():
				del self.jsonDict["servers"][serverid]["updated"][msgtype]
				everythingok = True
			self.jsonDict["servers"][serverid]["updated"][msgtype] = [stored.channel.id,stored.id]
			self.saveData()
			return everythingok
		else:
			self.newServer(serverid)
			self.addNotificationMessage(serverid,message,stored,key)
	def removeNotificationMessage(self, serverid, messageType):
		if serverid in self.jsonDict["servers"].keys():
			del self.jsonDict["servers"][serverid]["updated"][messageType]
			self.saveData()
			return True
		return False

#logs
	def setLogChannel(self,serverid,channelid):
		everythingok = False
		serverid = str(serverid)
		if serverid in self.jsonDict["servers"].keys():
			self.jsonDict["servers"][serverid]["log"] = channelid
			self.saveData()
			everythingok = True
		else:
			self.newServer(serverid)
			self.setLogChannel(serverid,channelid)
			everythingok = True
		return everythingok
	def removeLogChannel(self,serverid):
		serverid = str(serverid)
		if serverid in self.jsonDict["servers"].keys():
			self.jsonDict["servers"][serverid]["log"] = ""
			self.saveData()
			return True
		return False
	def logChannelCheck(self, message, client, bool_id=False):
		usedid = message
		if not bool_id:
			usedid = message.guild.id
		if str(usedid) in self.jsonDict["servers"].keys():
			if self.jsonDict["servers"][str(usedid)]["log"] != "":
				return client.get_channel(int(self.jsonDict["servers"][str(usedid)]["log"]))

		return None
#server
	def newServer(self,serverid):
		serverid = str(serverid)
		if serverid not in self.jsonDict["servers"].keys():
			self.jsonDict["servers"][serverid] = {}
			self.jsonDict["servers"][serverid]["updated"] = {}
			self.jsonDict["servers"][serverid]["notifications"] = {}
			self.jsonDict["servers"][serverid]["joinable_roles"] = []
			self.jsonDict["servers"][serverid]["log"] = ""
			self.saveData()
			return True
		return False
	def removeServer(self,serverid):
		serverid = str(serverid)
		del self.jsonDict["servers"][serverid]
		self.saveData()
		return True

	def serverInfo(self,serverid):
		serverid = str(serverid)
		msg = ""
		if "updated" in self.jsonDict["servers"][serverid]:
			msg = msg+"  **Update messages:**\n"
			for i,s in self.jsonDict["servers"][serverid]["updated"].items():
				msg = msg+"Update message Type: "+i+"\n"
				msg = msg+"Update message Channel: <#"+str(s[0])+">\n\n"
		if "notifications" in self.jsonDict["servers"][serverid]:
			msg = msg+"  **Notifications:**\n"
			for i,l in self.jsonDict["servers"][serverid]["notifications"].items():
				msg = msg+"    "+i.capitalize()+": "+l+"\n"
		return msg

#save / load
	def saveData(self,):
		fo = open(self.script_dir+"database.json", "w")
		fo.write(json.dumps(self.jsonDict, sort_keys=True, indent=4))
		fo.close()
		self.loadData()
	def loadData(self,):
		with open(self.script_dir+"database.json") as f:
			self.jsonDict = json.load(f)
			self.keywords = self.jsonDict["updated_messages"]["mentions"]["other"]
			self.updatedmessages= self.jsonDict["updated_messages"]["messages"]
			tmp = []
			for i in self.jsonDict["updated_messages"]["mentions"]["fissure"]["eras"]:
				for j in self.jsonDict["updated_messages"]["mentions"]["fissure"]["missions"]:
					tmp.append(i+""+j)
			self.keywords= self.keywords + tmp