#!/usr/bin/python
import discord
import asyncio
import random
import re
import os
from forever import utilities,database,helper,warframe,voice,gfl
from forever.wfmodules import wfmarket,droptables
###
# message, self,'e!', self.helper, self.sounds, self.wf, self.wfmarket, self.droptables, self.mathbot, self.util, self.db, self.vc
###
class Commands:
	class otherCommands:
		async def help(message, db, reg, helper, key):
			embed = ""
			if reg:
				embed = helper.embedMsg(key, db.jsonDict["updated_messages"], reg)
			else:
				embed = helper.embedMsg(key, db.jsonDict["updated_messages"], "main")
			await message.channel.send(embed=embed)
		async def avatar(message):
			if len(message.mentions) == 1:
				user = message.mentions[0]
				await message.channel.send(user.avatar_url)
		async def owo(message, db):
			var = None
			if message.mentions:
				var = message.author.name+" OwOes "+message.mentions[0].name
			else:
				var = message.author.name+" OwOes him/herself"
			em = discord.Embed(title=var)
			em.set_image(url=random.choice(db.jsonDict["images"]["owos"]))
			await message.channel.send(embed=em)
	class roleCommands:
		async def roleList(message, db):
			tmproles = {}
			for s in db.jsonDict["servers"][str(message.guild.id)]["joinable_roles"]:
				tmproles[s] = message.guild.get_role(int(s))
			em = discord.Embed(title="Joinable roles for "+message.guild.name, description="\n".join([s.name for x,s in tmproles.items()]))
			await message.channel.send(embed=em)
		async def joinRole(message, db, reg):
			for s in db.jsonDict["servers"][str(message.guild.id)]["joinable_roles"]:
				role = message.guild.get_role(int(s))
				if role.name.lower() == reg.group(2).lower():
					await message.author.add_roles(role)
					await message.add_reaction("☑️")
					break
		async def leaveRole(message, db, reg):
			for s in db.jsonDict["servers"][str(message.guild.id)]["joinable_roles"]:
				role = message.guild.get_role(int(s))
				if reg.group(2).lower() == role.name.lower():
					if role in message.author.roles:
						await message.author.remove_roles(role)
						await message.add_reaction("☑️")
						break
	class nsfwCommands:
		async def rule34(message, util, key='!'):
			if message.channel.is_nsfw():
				var = ""
				if key+'rule34' in message.content:
					var = 'rule34'
				link = util.APIOpen(message, var, key)
				em = discord.Embed(title=var.capitalize(),colour=0x8A00E0)
				em.set_image(url=link)
				await message.channel.send(embed=em)
	class modCommands:
		async def serverinfo(message, db):
			msg = """
			**Owner:** {owner}\n
			**Emojis:**
			{emojis}
			**AFK Channel:** {afkchannel}\n
			**Total Channel/Category Count:** {totalchannelcount}
			**Total Categories:** {categoriescount}
			**Voice Channel Count:** {voicechannelcount}
			**Text Channel Count:** {textchannelcount}\n
			**Member Count:** {membercount}\n\n
			**Bot Related:**\n{botserverinfo}""".format(
				owner=str(message.guild.owner),
				emojis=" ".join([str(x) for x in message.guild.emojis]),
				afkchannel=str(message.guild.afk_channel) if message.guild.afk_channel else "N/A",
				totalchannelcount=len(message.guild.channels),
				categoriescount=len(message.guild.categories),
				voicechannelcount=len(message.guild.voice_channels),
				textchannelcount=len(message.guild.text_channels),
				membercount=len(message.guild.members),
				botserverinfo=db.serverInfo(message.guild.id))
			em = discord.Embed(title=message.guild.name,description=msg,colour=0x8A00E0)
			await message.channel.send( embed=em)
		async def copyChannel(message, client, util, reg):
			reg1 = int(reg.group(1).replace("<#","").replace(">",""))
			reg2 = int(reg.group(2).replace("<#","").replace(">",""))
			reg1 = client.get_channel(reg1)
			reg2 = client.get_channel(reg2)
			await message.add_reaction("☑️")
			await util.channelCopy(reg1, reg2)
		def addJoinableRoles(message, db):
			ids = [x.id for x in message.role_mentions]
			for s in ids:
				if str(s) not in db.jsonDict["servers"][str(message.guild.id)]["joinable_roles"]:
					db.addRole(str(message.guild.id),str(s))
		def removeJoinableRoles(message, db):
			ids = [x.id for x in message.role_mentions]
			for s in ids:
				if str(s) in db.jsonDict["servers"][str(message.guild.id)]["joinable_roles"]:
					db.removeRole(str(message.guild.id),str(s))
		async def purge(message, key):
			amountsOfDel = message.content[len(key+'empty'):].strip()
			amountsOfDel = int(amountsOfDel)+1
			try:
				deleted = await message.channel.purge(limit=amountsOfDel)
			except Exception as e:
				print(e)
async def commandRead(class_vars):
#
	message  	= class_vars["message"]
	client 		= class_vars["client"]
	key			= class_vars["key"]
	helper		= class_vars["helper"]
	sounds		= class_vars["sounds"]
	gfl			= class_vars["gfl"]
	wf 			= class_vars["wf"]
	wfmarket	= class_vars["wfmarket"]
	droptables	= class_vars["droptables"]
	mathbot		= class_vars["mathbot"]
	util		= class_vars["util"]
	db 			= class_vars["db"]
	vc 			= class_vars["vc"]
	
	commands = Commands()
#bot admin
	#if message.author.id in db.jsonDict["bot-admins"]:
	#	"prin"
#misc
	if util.commandCheck(message,['help','assistance'],key):
		reg = re.match(key+"(help|assistance)\s(\S*)\s?(\d)?",message.content,re.M|re.I)
		await commands.otherCommands.help(message, db, reg, helper, key)
	if util.commandCheck(message,['avatar'],key):
		await commands.otherCommands.avatar(message)
	if util.commandCheck(message,['owo'],key):
		await commands.otherCommands.owo(message, db)
#role commands
	if util.commandCheck(message,['roles', 'role list'],key):
		await commands.roleCommands.roleList(message, db)
	if util.commandCheck(message,['join','role join'],key):
		reg = re.match(key+"(join|role\sjoin)\s(.*)",message.content)
		if reg:
			await commands.roleCommands.joinRole(message, db, reg)
		
	if util.commandCheck(message,['leave', 'role leave'],key):
		reg = re.match(key+"(leave|role\sleave)\s(.*)",message.content)
		if reg:
			await commands.roleCommands.leaveRole(message, db, reg)
#voice class: classes/voice.py
		#play voice via youtube link
	if message.guild != None:
		if util.commandCheck(message,['play'],key):
			if message.author.voice != None:
				if message.author.voice.channel != None:
					reg = re.match(key+"play (http[s]?://(www\.)?(youtube\.com|youtu\.be)/(watch\?.*v=)?.*)", message.content)
					if reg != None:
						if str(message.guild.id) not in vc.keys():
							notfound = True
							for x in client.voice_clients:
								if message.guild.id == x.guild.id:
									if x.is_connected():
										vc[str(message.guild.id)] = voice.Voice(x, message.channel)
										notfound = False
							if notfound:
								vc[str(message.guild.id)] = voice.Voice(await message.author.voice.channel.connect(),message.channel)
								await vc[str(message.guild.id)].addtoPlaylist(reg.group(1))
								
									
						else:
							await vc[str(message.guild.id)].addtoPlaylist(reg.group(1))
			print(vc)
		if util.commandCheck(message,['skip'],key):
			if str(message.guild.id) in vc.keys():
				await vc[str(message.guild.id)].skip()
						
		#pause audio stream
		if util.commandCheck(message,['pause'],key):
			if str(message.guild.id) in vc.keys():
				await vc[str(message.guild.id)].pause()
		#resume audio stream
		if util.commandCheck(message,['resume'],key):
			if str(message.guild.id) in vc.keys():
				await vc[str(message.guild.id)].resume()
		if util.commandCheck(message,['playlist'],key):
			if str(message.guild.id) in vc.keys():
				await vc[str(message.guild.id)].show_playlist()
		#list available audiofiles
		if util.commandCheck(message,['sounds','mp3s'],key):
			em = discord.Embed(title="Sounds",description="\n".join(sorted(sounds.keys())))
			await message.channel.send(embed=em)
		#play audio files
		if message.content in sounds.keys():
			if str(message.guild.id) not in vc.keys():
				vc[str(message.guild.id)] = voice.Voice(await message.author.voice.channel.connect(), message.channel)
			await vc[str(message.guild.id)].playFile(sounds[message.content])
			await message.delete()
#mod classes/database.py
		if message.author.guild_permissions.administrator:
			if util.commandCheck(message,['server'],key):
				await commands.modCommands.serverinfo(message, db)
			if util.commandCheck(message,['copy channel'],key):
				reg = re.match(key+"copy channel\s(.*)\s(.*)", message.content)
				if reg:
					await commands.modCommands.copyChannel(message, client, util, reg)

			#logs
			if util.commandCheck(message,['set log'],key):
				if db.setLogChannel(str(message.guild.id),str(message.channel.id)):
					await message.add_reaction("☑️")
				else:
					await message.add_reaction("❌")
			if util.commandCheck(message,['remove log'],key):
				if db.removeLogChannel(str(message.guild.id)):
					await message.add_reaction("☑️")
				else:
					await message.add_reaction("❌")


			if util.commandCheck(message,['add role'],key):
				try:
					commands.modCommands.addJoinableRoles(message, db)
					await message.add_reaction("☑️")
				except:
					await message.add_reaction("❌")
			if util.commandCheck(message,['remove role'],key):
				try:
					commands.modCommands.removeJoinableRoles(message, db)
					await message.add_reaction("☑️")
				except:
					await message.add_reaction("❌")

						
		if message.author.guild_permissions.manage_channels:

			if util.commandCheck(message,['purge','empty'],key):
				await commands.modCommands.purge(message, key)

			if util.commandCheck(message,['create message'],key):
				reg = re.match(key+"create message\s(\w*)",message.content,re.M|re.I)
				if reg:
					if reg.group(1).lower() in db.jsonDict["updated_messages"]["messages"]:
						msg = await message.channel.send(embed=discord.Embed(title="SoonTM"))
						if db.addNotificationMessage(message.guild.id, msg, reg.group(1).lower()):
							await message.add_reaction("☑️")
						else:
							await message.add_reaction("❌")


			#create binds for certain message types
			if util.commandCheck(message,['create bind'],key):
				roles = message.role_mentions
				if len(roles) > 0:
					reg = re.match(key+"create bind\s(.*)\s.*",message.content,re.M|re.I)
					if reg != None:
						if db.bindJSON(reg.group(1),"<@&"+str(roles[0].id)+">",message.guild.id):
							await message.add_reaction("☑️")
						else:
							await message.add_reaction("❌")
						
			#remove bind x
			if util.commandCheck(message,['remove bind'],key):
				reg = re.match(key+"remove bind\s(\w*)",message.content,re.M|re.I)
				if reg != None:
					if db.removeBindJSON(reg.group(1),message.guild.id):
						await message.add_reaction("☑️")
					else:
						await message.add_reaction("❌")

			if util.commandCheck(message, ['bind list'], key):
				await message.channel.send(embed=db.bindList())
	
#nsfw
	if util.commandCheck(message,['rule34'],key):
		await commands.nsfwCommands.rule34(message, util, key)
#math and/or warframe stuff classes/mathBot.py
	#probability of x trials x drops and x chance, huge thanks to Sleimok
	if util.commandCheck(message,['probability'],key):
		await message.channel.send( mathbot.probability(message.content,key))

	#calculate armor's damage resistance, usage: key+armor->res% (armor)
	if util.commandCheck(message,['armor-res','armordmgreduction'],key):
		stripped = message.content.split(" ")
		await message.channel.send("Damage reduction:"+str(mathbot.damageReduction(int(stripped[1]))))

	#calculate armor's effective hp usage: key+armor->ehp (armor) (health)
	if util.commandCheck(message,['armor-ehp','ehparmor'],key):
		stripped = message.content.split(" ")
		await message.channel.send("Effective health:"+str(mathbot.effectiveHPArmor(int(stripped[1]),int(stripped[2]))))
	
	#calculate damage reduction to effective hp usage: key+reduction->ehp (reduction) (hp)
	if util.commandCheck(message,['reduction-ehp','ehpreduction'],key):
		stripped = message.content.split(" ")
		await message.channel.send("Effective health:"+str(mathbot.effectiveHPReduction(float(stripped[1]),int(stripped[2]))))
	
	#calculate Frost's snowglobe HP usage: key+frostglobe (armormultiplier from mods) (extra pwrstr) (extra armor, ex. guardian)
	if util.commandCheck(message,['frostglobe','frost-globe'],key):
		stripped = message.content.split(" ")
		if len(stripped)>=3:
			var=0
			if len(stripped)==4:
				var=stripped[3]
			await message.channel.send("Frost Globe HP is "+str(mathbot.frostGlobe(float(stripped[1]),float(stripped[2]),int(var))))
#builds for warframes classes/warframe.py
	if util.commandCheck(message,['build'], key):
		await wf.sendBuildItems(message, key, 'build')
	if util.commandCheck(message,['loadout-build'],key):
		await wf.sendBuildBundle(message, key, 'loadout-build')

	#wfmarket thingy classes/dataClasses/wfmarket_item.py
	if util.commandCheck(message,['price'],key):
		reg = re.match(key+"price\s(.*)",message.content,re.M|re.I)
		if reg != None:
			var = await wfmarket.getPrice(reg.group(1))
			if var != None:
				if len(var) == 2:
					em = discord.Embed(title=reg.group(1))
					em.add_field(name="Buy average",value=var[0],inline=False)
					em.add_field(name="Sell average",value=var[1],inline=False)
					await message.channel.send(embed=em)
#wf market
	#classes/wfmodules/wfmarket.py
	if util.commandCheck(message,['wfitems'],key):
		fo = open("/home/dss/project/discordbot/items.txt","w+")
		fo.write("\n".join(sorted([x for x in wfmarket.wfitems.keys()])))
		fo.close()
		await message.channel.send(file=discord.File("/home/dss/project/discordbot/items.txt","items.txt"))
		
		os.remove("/home/dss/project/discordbot/items.txt")
	#classes/wfmodules/wfmarket.py
	if util.commandCheck(message,['relic worth','relicworth'],key):
		reg = re.match(key+"relic\s?worth\s(.*)",message.content,re.M|re.I)
		if reg != None:
			var = await wfmarket.mapRelic(reg.group(1).title())
			em = discord.Embed(title=reg.group(1).title())
			for j,k in var.items():
				if k == None:
					continue
				em.add_field(name=j,value="Buyer average:"+str(k[0])+"\nSeller average:"+str(k[1]),inline=False)
			await message.channel.send(embed=em)
#droptables classes/wfmodules/droptables.py

	#relics
	if util.commandCheck(message,['relic list','reliclist'],key):
		relics = droptables.requestKeys("Relics")
		msg = ""
		axi = ""
		neo = ""
		meso = ""
		lith = ""
		reg = re.match(key+"relic\s?list\s(.*)",message.content,re.M|re.I)
		if reg != None:
			if relics != None:
				for i in sorted(relics):
					if reg.group(1) == "axi":
						if "axi" in i.lower():
							axi = axi + i +"\n"
					if reg.group(1) == "neo":
						if "neo" in i.lower():
							neo = neo + i +"\n"
					if reg.group(1) == "meso":
						if "meso" in i.lower():
							meso = meso + i +"\n"
					if reg.group(1) == "lith":
						if "lith" in i.lower():
							lith = lith + i +"\n"
				msg = axi+neo+meso+lith
				if len(msg) > 0:
					em = discord.Embed(title=reg.group(1).capitalize(),description=msg+"Choose relic via command "+key+"crelic *relic's name*",colour=0x8A00E0)
					await message.channel.send(embed=em)


	if util.commandCheck(message,["relic show"],key):
		relics = droptables.requestKeys("Relics")
		reg = re.match(key+"relic show\s(.*)",message.content,re.M|re.I)
		relicname = reg.group(1)
		if "relic" not in relicname.lower():
			relicname = relicname +" Relic"
		if relicname.title() in relics:
			req = droptables.requestTable("Relics",relicname.title())
			em = discord.Embed(title=reg.group(1).title(),colour=0x8A00E0)
			for j,k in sorted(req.items()):
				em.add_field(name=j,value=''.join(x+"\n" for x in k))
			await message.channel.send(embed=em)


	if util.commandCheck(message,["bounty list","bountylist"],key):
		reg = re.match(key+"bounty\s?list\s(.*)",message.content,re.M|re.I)
		bounties = ""
		if reg != None:
			if reg.group(1).lower() in ["cetus","vallis"]:
				if reg.group(1).lower() == "cetus":
					bounties = droptables.requestKeys("Cetus Bounty Rewards")
				elif reg.group(1).lower() == "vallis":
					bounties = droptables.requestKeys("Orb Vallis Bounty Rewards")
				em = discord.Embed(title=reg.group(1).title(),description=''.join(x+"\n" for x in sorted(bounties))+"Choose bounty via "+key+"cbounty *bounty*")
				await message.channel.send( embed=em)


	if util.commandCheck(message,["bounty rewards","bountyrewards"],key):
		bounties = ""
		reg= re.match(key+"bounty\s?rewards\s(.*)",message.content,re.M|re.I)
		var = ""
		if "vallis" in message.content.lower():
			var = "Orb Vallis Bounty Rewards"
		elif "cetus" in message.content.lower() or "ghoul" in message.content.lower():
			var = "Cetus Bounty Rewards"
		bounties = droptables.requestKeys(var)
		if bounties != False:
			if reg.group(1) in bounties:
				bounty = droptables.requestTable(var,reg.group(1).title())
				em = discord.Embed(title=reg.group(1).title())
				for j,k in sorted(bounty.items()):
					msg = ""
					for x,y in sorted(k.items()):
						msg = msg + "**"+x+"**\n"
						for i in y:
							msg = msg + i +"\n"
					em.add_field(name=j,value=msg)
				await message.channel.send(embed=em)


	if util.commandCheck(message,['enemy list','enemylist'],key):
		fo = open("/home/dss/project/discordbot/enemylist.txt","w+")
		fo.write("\n".join(sorted(droptables.requestKeys("Mod Drops by Enemy"))))
		fo.close()
		await message.channel.send(file=discord.File("/home/dss/project/discordbot/enemylist.txt","enemylist.txt"))
		os.remove("/home/dss/project/discordbot/enemylist.txt")
	
	if util.commandCheck(message,['enemy drops','enemydrops'],key):
		reg = re.match(key+"enemy\s?drops\s(.*)",message.content,re.M|re.I)
		if reg:
			var = reg.group(1).lower().replace("profit-taker orb", "profit-taker").replace("capture", "special").title()
			name = reg.group(1).title()
			em = discord.Embed(title="Enemy Droptable: "+name)
		#keys
			modkeys = droptables.requestKeys("Mod Drops by Enemy")
			if var in modkeys:
				mods = droptables.requestTable("Mod Drops by Enemy",var)
				adding = ""
				for j,k in mods.items():
					adding = adding+"\n**"+j+"**"
					for s in k:
						adding = adding +"\n"+ s
				em.add_field(name="Mods",value=adding)
			resourcekeys = droptables.requestKeys("Resource Drops by Enemy")
			if var in resourcekeys:
				resource = droptables.requestTable("Resource Drops by Enemy",var)
				adding = ""
				for j,k in resource.items():
					adding = adding + "\n**"+j+"**"
					for s in k:
						adding = adding +"\n"+s 
				em.add_field(name="Resources",value=adding)
			partskeys = droptables.requestKeys("Blueprint/Item Drops by Enemy")
			if var in partskeys:
				parts = droptables.requestTable("Blueprint/Item Drops by Enemy",var)
				adding = "**"+parts[0]+"**\n"
				del parts[0]
				for s in parts:
					adding = adding +"\n"+s
				em.add_field(name="Parts",value=adding)

			sigilkeys = droptables.requestKeys("Sigil Drops by Enemy")
			if var in sigilkeys:
				sigil = droptables.requestTable("Sigil Drops by Enemy",var)
				adding = ""
				for j,k in sigil.items():
					k = k.replace("%","%;")
					k = k.split(";")
					adding = adding+"**"+j+"**\n"+"\n".join(k)
				em.add_field(name="Sigil Drops",value=adding)
			additional = None
			additionalkeys = droptables.requestKeys("Additional Item Drops by Enemy")
			if var in additionalkeys:
				additional = droptables.requestTable("Additional Item Drops by Enemy",var)
				adding = ""
				for j,k in additional.items():
					adding = adding+"\n**"+j+"**\n"
					for s in k:
						adding = adding+"\n"+s
				em.add_field(name="Additional Item Drops",value=adding)
		#sending msg
			await message.channel.send(embed=em)
#gfl
	if util.commandCheck(message,['gfl'],key):
		if await gfl.parse(message, key):
			await message.add_reaction("☑️")
		else:
			await message.add_reaction("❌")


