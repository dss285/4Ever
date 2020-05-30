import asyncio
import aiohttp
import re
import json
import os
from bs4 import BeautifulSoup
async def dropRates():
	datadir = "/home/dss/data/"
	async with aiohttp.ClientSession() as sess:
		async with sess.get("https://n8k6e2y6.ssl.hwcdn.net/repos/hnfvc0o3jnfvc873njb03enrf56.html") as r:
			if r.status==200:
				droptables = {}
				parsing = await r.text()
				listed = parsing.split("<h3")
				del listed[0]
				del listed[0]
				del listed[0]
				for i in listed:
					split = i.split("</h3>")
					name = split[0].split("\">")[1]
					name = name.strip(":")
					splitted = split[1]
					if "html" in splitted:
						splitted = splitted[:-len("</body></html>")]
					soup = BeautifulSoup(splitted,"lxml")
					table = soup.findAll('table')
					if table:
						rows = table[0].findAll('tr')
						droptables[name] = {}
						if name=="Sorties":
							del rows[0]
							for x in rows:
								cells = x.findAll('td')
								if len(cells) == 2:
									droptables[name][cells[0].getText()] = cells[1].getText()
						elif name=="Keys":
							lst = ''.join([str(x) for x in rows])
							lst = lst.split("<tr class=\"blank-row\"><td class=\"blank-row\" colspan=\"2\"></td></tr>")
							del lst[len(lst)-1]
							tmp = {}
							for x in lst:
								x = x.replace("<tr><th colspan=\"2\">","").replace("</th></tr><tr><th colspan=\"2\">",";;").replace("</th></tr><tr><td>","::").replace("</td><td>"," ")
								x = x.replace("</td></tr><tr><th colspan=\"2\">",";;").replace("</td></tr>","").replace("</th></tr>",";-").replace("<tr><td>"," ")
								x = re.sub("(Rotation [ABC])",r";;\1;;",x)
								x = x.split(";-")
								if len(x)>=2:
									tmp[x[0]] = x[1].split("::")
								else:
									x=x[0].split("::")
									tmp[x[0]] = x[1]
							droptables["Keys"]=tmp
						elif name=="Resource Drops by Resource":
							lst = ''.join([str(x) for x in rows])
							lst = lst.split("<tr class=\"blank-row\"><td class=\"blank-row\" colspan=\"3\"></td></tr>")
							del lst[len(lst)-1]
							tmp = {}
							for x in lst:
								x = x.replace("</th></tr><tr><th>Enemy Name</th><th>Resource Drop Chance</th><th>Chance</th></tr><tr><td>","::").replace("<tr><th colspan=\"3\">","").replace("</td><td>"," ")
								x = x.replace("</td></tr><tr><td>",";;").replace("</td></tr>","")
								x = x.split("::")
								tmp[x[0]] = x[1].split(";;")
							droptables["Resource Drops by Resource"] = tmp
						elif name=="Keys":
							lst = ''.join([str(x) for x in rows])
							lst = lst.split("<tr class=\"blank-row\"><td class=\"blank-row\" colspan=\"2\"></td></tr>")
							del lst[len(lst)-1]
							tmp = {}
							for x in lst:
								x = x.replace("<tr><th colspan=\"2\">","").replace("</th></tr><tr><th colspan=\"2\">",";;").replace("</th></tr><tr><td>","::").replace("</td><td>"," ")
								x = x.replace("</td></tr><tr><th colspan=\"2\">",";;").replace("</td></tr>","").replace("</th></tr>",";-").replace("<tr><td>"," ")
								x = re.sub("(Rotation [ABC])",r";;\1;;",x)
								x = x.split(";-")
								if len(x)>=2:
									tmp[x[0]] = x[1].split("::")
								else:
									x=x[0].split("::")
									tmp[x[0]] = x[1]
							droptables["Keys"]=tmp
						elif name=="Missions":
							lst = ''.join([str(x) for x in rows])
							lst = lst.split("<tr class=\"blank-row\"><td class=\"blank-row\" colspan=\"2\"></td></tr>")
							del lst[len(lst)-1]
							tmp = {}
							for x in lst:
								x = x.replace("<tr><th colspan=\"2\">","").replace("</th></tr><tr><th colspan=\"2\">",";-").replace("</th></tr><tr><td>","-;")
								x = x.replace("</th></tr><tr><td>",";;").replace("</td><td>"," ").replace("</td></tr>","").replace("<tr><td>",";;;").replace("</th></tr>Rotation","-|;Rotation")
								x = x.replace("%)R","% -|;R")
								x = x.split("-|;")
								if "-;" in x[0]:
									var = x[0].split("-;")
									x.append(var[1])
									var = var[0]
								else:
									var = x[0]
								del x[0]
								tmp[var] = [s.split("-;") for s in x]
							droptables["Missions"]=tmp
						elif name=="Additional Item Drops by Enemy":
							lst = ''.join([str(x) for x in rows])
							lst = lst.replace("(","").replace(")","")
							lst = lst.split("<tr class=\"blank-row\"><td class=\"blank-row\" colspan=\"3\"></td></tr>")
							del lst[len(lst)-1]
							tmp = {}
							for x in lst:
								x = x.replace("<tr><th>","").replace("</th><th colspan=\"2\">Additional Item Drop Chance:",";-")
								x = x.replace("</th></tr><tr><td></td><td>","-;").replace("</td><td>"," ").replace("</td></tr>","").replace("<tr><td>","::")
								x = x.split(";-")
								x[1] = x[1].split("-;")
								tmp[x[0]] = {x[1][0]:x[1][1].split("::")}
							droptables["Additional Item Drops by Enemy"] = tmp
						elif name=="Resource Drops by Enemy":
							lst = ''.join([str(x) for x in rows])
							lst = lst.replace("(","").replace(")","")
							lst = lst.split("<tr class=\"blank-row\"><td class=\"blank-row\" colspan=\"3\"></td></tr>")
							del lst[len(lst)-1]
							tmp = {}
							for x in lst:
								x = x.replace("<tr><th>","").replace("</th><th colspan=\"2\">",":;:").replace("</th></tr><tr><td></td><td>","").replace("</td><td>",";:;").replace("</td></tr>","").replace("<tr><td>","")
								x = x.split(":;:",1)
								x[1] = x[1].replace("%","% :;:").split(":;:",1)
								tmp[x[0]] = {x[1][0]:[s.replace(";:;"," ").replace(" :;:","")for s in x[1][1].split(":;:;:;")]}
							droptables["Resource Drops by Enemy"] = tmp
						elif name=="Sigil Drops by Enemy":
							lst = ''.join([str(x) for x in rows])
							lst = lst.replace("(","").replace(")","")
							lst = lst.split("<tr class=\"blank-row\"><td class=\"blank-row\" colspan=\"3\"></td></tr>")
							tmp = {}
							del lst[len(lst)-1]
							for x in lst:
								x = x.replace("<tr><th>","").replace("</th><th colspan=\"2\">","").replace("</th></tr><tr><td></td><td>","").replace("</td><td>"," ").replace("</td></tr>","").replace("<tr><td> ","")
								x = x.split("Sigil Drop Chance:")
								x[1] = x[1].replace("%","% ").split(" ", 2)
								del x[1][0]
								tmp[x[0]] = {x[1][0] : x[1][1]}
							droptables["Sigil Drops by Enemy"] = tmp
						elif name=="Blueprint/Item Drops by Blueprint/Item":
							lst = ''.join([str(x) for x in rows])
							lst = lst.replace("(","").replace(")","")
							lst = lst.split("<tr class=\"blank-row\"><td class=\"blank-row\" colspan=\"3\"></td></tr>")
							del lst[len(lst)-1]
							tmp = {}
							for x in lst:
								x = x.replace("<tr><th colspan=\"3\">","").replace("</th></tr><tr><th>Enemy Name</th><th>Blueprint/Item Drop Chance</th><th>Chance</th></tr><tr><td>","||")
								x = x.replace("<tr><td>","-_-").replace("</td><td>",";:;").replace("</td><td>",":;:").replace("</td></tr>","")
								x = x.split("||")
								x[1] = x[1].split(";:;",1)
								x[1][1]= x[1][1].replace(";:;","").split("-_-")
								tmp[x[0]] = {x[1][0]:x[1][1]}
							droptables["Blueprint/Item Drops by Blueprint/Item"] = tmp
						elif name=="Blueprint/Item Drops by Enemy":
							lst = ''.join([str(x) for x in rows])
							lst = lst.replace("(","").replace(")","")
							lst = lst.split("<tr class=\"blank-row\"><td class=\"blank-row\" colspan=\"3\"></td></tr>")
							tmp = {}
							for x in lst:
								x = x.replace("<tr><th>","").replace("</th><th colspan=\"2\">","").replace("</th></tr><tr><td></td><td>","")
								x = x.replace("</td><td>","").replace("</td>","").replace("</tr>","").replace("<tr><td>","")
								x = x.split(":")
								if len(x) > 1:
									x[0] = x[0].replace("Blueprint",":Blueprint")
									x[0] = x[0].split(":")
									x[0][0] = x[0][0].replace("Wolf Of Saturn Six", "Daddy Of Saturn Six")
									x[1] = x[1].replace("%","%:").split(":")
									x[1] = [s for s in x[1] if s != ""]
									tmp[x[0][0]] = x[1]
							droptables["Blueprint/Item Drops by Enemy"] = tmp
						elif name=="Mod Drops by Enemy":
							lst = ''.join([str(x) for x in rows])
							lst = lst.replace("(","").replace(")","")
							lst = lst.split("<tr class=\"blank-row\"><td class=\"blank-row\" colspan=\"3\"></td></tr>")
							del lst[len(lst)-1]
							tmp = {}
							for x in lst:
								x = x.replace("<tr><th>","").replace("</th><th colspan=\"2\">Mod Drop Chance: ",";-")
								x = x.replace("</th></tr><tr><td></td><td>","-;").replace("</td></tr><tr><td></td><td>",";;")
								x = x.replace("</td><td>"," ").replace("</td></tr>","")
								x = x.split(";-")
								x[1] = x[1].split("-;")
								x[1][1] = x[1][1].split(";;")
								tmp[x[0]] = {x[1][0]:x[1][1]}
							droptables["Mod Drops by Enemy"] = tmp
						elif name=="Mod Drops by Mod":
							lst = ''.join([str(x) for x in rows])
							lst = lst.replace("(","").replace(")","")
							lst = lst.split("<tr class=\"blank-row\"><td class=\"blank-row\" colspan=\"3\"></td></tr>")
							del lst[len(lst)-1]
							tmp = {}
							for x in lst:
								x = x.replace("<tr><th colspan=\"3\">","").replace("</th></tr><tr><th>Enemy Name</th><th>Mod Drop Chance</th><th>Chance</th></tr><tr><td>",";-")
								x= x.replace("</td><td>"," ").replace("</td></tr><tr><td>",";;").replace("</td></tr>","")
								x=x.split(";-")
								x[1] = x[1].split(";;")
								tmp[x[0]] = x[1]
							droptables["Mod Drops by Mod"] = tmp
						elif name=="Cetus Bounty Rewards":
							lst = ''.join([x.getText() for x in rows])
							lst = re.sub("(Rotation [ABC])",r"::\1",lst)
							lst = lst.replace("Level","::Level")
							lst = lst.split("::")
							del lst[0]
							cetusbounties = {}
							cetusbounties[lst[0]] = [lst[i] for i in range(1,4)]
							cetusbounties[lst[4]] = [lst[i] for i in range(5,8)]
							cetusbounties[lst[8]] = [lst[i] for i in range(9,12)]
							cetusbounties[lst[12]] = [lst[i] for i in range(13,16)]
							cetusbounties[lst[16]] = [lst[i] for i in range(17,20)]
							cetusbounties[lst[20]] = [lst[i] for i in range(21,22)]
							cetusbounties[lst[22]] = [lst[i] for i in range(23,24)]
							for j,k in cetusbounties.items():
								temp = {}
								for i in k:
									i = re.sub("(Rotation [ABC])",r"\1::",i)
									i = i.split("::")
									temp[i[0]] = {}
									s = i[1]
									s = s.replace("Stage 1","Stage 1::")
									s = s.replace("Stage 2, Stage 3 of 4, and Stage 3 of 5","::Stage 2, Stage 3 of 4, and Stage 3 of 5::")
									s = s.replace("Stage 4 of 5","::Stage 4 of 5::")
									s = s.replace("Final Stage","::Final Stage::")
									lst = s.split("::")
									temp[i[0]][lst[0]] = lst[1].replace("(","").split(")")
									temp[i[0]][lst[2]] = lst[3].replace("(","").split(")")
									temp[i[0]][lst[4]] = lst[5].replace("(","").split(")")
									temp[i[0]][lst[6]] = lst[7].replace("(","").split(")")
								cetusbounties[j] = temp
							droptables["Cetus Bounty Rewards"]	= cetusbounties
						elif name=="Orb Vallis Bounty Rewards":
							lst = ''.join([x.getText() for x in rows])
							lst = re.sub("(Rotation [ABC])",r"::\1",lst)
							lst = lst.replace("Level","::Level")
							lst = lst.split("::")
							del lst[0]
							vallisbounties = {}
							vallisbounties[lst[0]] = [lst[i] for i in range(1,4)]
							vallisbounties[lst[4]] = [lst[i] for i in range(5,8)]
							vallisbounties[lst[8]] = [lst[i] for i in range(9,12)]
							vallisbounties[lst[12]] = [lst[i] for i in range(13,16)]
							vallisbounties[lst[16]] = [lst[i] for i in range(17,20)]
							for j,k in vallisbounties.items():
								temp = {}
								for i in k:
									i = re.sub("(Rotation [ABC])",r"\1::",i)
									i = i.split("::")
									temp[i[0]] = {}
									s = i[1]
									s = s.replace("Stage 1","Stage 1::")
									s = s.replace("Stage 2, Stage 3 of 4, and Stage 3 of 5","::Stage 2, Stage 3 of 4, and Stage 3 of 5::")
									s = s.replace("Stage 4 of 5","::Stage 4 of 5::")
									s = s.replace("Final Stage","::Final Stage::")
									lst = s.split("::")
									temp[i[0]][lst[0]] = lst[1].replace("(","").split(")")
									temp[i[0]][lst[2]] = lst[3].replace("(","").split(")")
									temp[i[0]][lst[4]] = lst[5].replace("(","").split(")")
									temp[i[0]][lst[6]] = lst[7].replace("(","").split(")")
								vallisbounties[j] = temp
							droptables["Orb Vallis Bounty Rewards"]	= vallisbounties
						elif name=="Relics":
							i = 0
							relics = []
							while i < len(rows):
								var = rows[i].getText()
								i+=1
								var = var+";;;"+rows[i].getText()
								i+=1
								var = var+";;;"+rows[i].getText()
								i+=1
								var = var+";;;"+rows[i].getText()
								i+=1
								var = var+";;;"+rows[i].getText()
								i+=1
								var = var+";;;"+rows[i].getText()
								i+=1
								var = var+";;;"+rows[i].getText()
								i+=2
								relics.append(var)
							for i in relics:
								splitted = i.split(";;;")
								relic=splitted[0]
								rarity=relic.replace("(","").replace(")","").replace("Relic ","Relic;;").split(";;")
								relic = rarity[0]
								rarity = rarity[1]
								del splitted[0]
								if relic not in droptables[name].keys():
									droptables[name][relic] = {}
									droptables[name][relic][rarity] = splitted
								else:
									if rarity not in droptables[name][relic].keys():
										droptables[name][relic][rarity] = splitted
						elif name=="Dynamic Location Rewards":
							lst = ''.join([x.getText() for x in rows])
							lst = lst.replace("Arbitrations","Arbitrations:")
							lst = lst.replace("Derelict Vault",";;Derelict Vault:")
							lst = lst.replace("Phorid Assasination",";;Phorid Assasination:")
							lst = lst.replace("Nightmare Mode Rewards",";;Nightmare Mode Rewards:")
							lst = lst.replace("Fomorian Sabotage",";;Fomorian Sabotage:")
							lst = lst.replace("Razorback",";;Razorback:")
							lst = lst.split(";;")
							dynamiclocrewards={}
							for x in lst:
								splitted = x.split(":")
								name = splitted[0]
								splitted[1] = splitted[1].replace("Rotation A","Rotation A::")
								splitted[1] = splitted[1].replace("Rotation B","::Rotation B::")
								splitted[1] = splitted[1].replace("Rotation C","::Rotation C::")
								val = splitted[1]
								if "::" in splitted[1]:
									split2 = splitted[1].split("::")
									rotations = {}
									lst = split2[1].replace("(","").split(")")
									del lst[len(lst)-1]
									rotations[split2[0]] = lst
									lst = split2[3].replace("(","").split(")")
									del lst[len(lst)-1]
									rotations[split2[2]] = lst
									lst = split2[5].replace("(","").split(")")
									del lst[len(lst)-1]
									rotations[split2[4]] = lst
									val = rotations
								else:
									val = val.replace("(","").split(")")
									del val[len(val)-1]
								dynamiclocrewards[splitted[0]] = val
							droptables["Dynamic Location Rewards"] = dynamiclocrewards
				fo = open(datadir+'droptables.json', "w")
				fo.write(json.dumps(droptables, sort_keys=True, indent=0))
				fo.close()
