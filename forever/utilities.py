import urllib
import urllib.request
import forever
import xml.etree.ElementTree as ET
import random
import re
import traceback
import discord
#self.wfinfo, self.mentionhandler, self.wf, self.helper, self.db.jsonDict
class Utilities:
	def __init__(self,):
		self.voiceplayers = []
	def commandCheck(self,message,command,key='!'):
		for i in command:
			if message.content.startswith(key+i):
				return True
		return False
	def APIOpen(self, message, keyword, key):
		hdr = {"User-Agent" : "4Ever Discord Bot"}
		tags = message.content[len(key+keyword):].strip()
		tags = tags.replace(' ', '+')
		url = ""
		if keyword == "real":
			url = "https://realbooru.com/index.php?page=dapi&s=post&q=index&limit=100&tags="+tags
		elif keyword== "rule34":
			url = "https://rule34.xxx/index.php?page=dapi&s=post&q=index&limit=100&tags="+tags
		req = urllib.request.Request(url, headers=hdr)
		req2 = urllib.request.urlopen(req)
		parse = ET.parse(req2)
		list = [el.attrib.get('file_url') for el in parse.findall('.//post')]
		return random.choice(list)
	async def channelCopy(self, channel, targetchannel,amount=15):
		history = await channel.history(limit=amount).flatten()
		history.reverse()
		for message in history:
			content = message.content
			if message.attachments:
				for i in message.attachments:
					content = content +"\n"+i.url
			if message.embeds:
				await targetchannel.send(content=content,embed=message.embeds[0])
			else:
				try:
					await targetchannel.send(content)
				except discord.HTTPException:
					print("empty message?")
	async def loop(self, client, wfinfo, handler, wf, helper, db):
		for key, s in db["servers"].items():
			if s["updated"]:
				if "sorties" in s["updated"]:
					try:
						await wf.sorties(client, wfinfo, helper, key, s["updated"]["sorties"])
					except discord.NotFound as e:
						del s["updated"]["sorties"]
						print("msg removed sorties")
					except Exception as e:
						print(e)
						traceback.print_exc()
				if "nightwave" in s["updated"]:
					try:
						await wf.nightwave(client, wfinfo, key, s["updated"]["nightwave"])
					except discord.NotFound as e:
						del s["updated"]["nightwave"]
						print("msg removed nw")
					except Exception as e:
						print(e)
						traceback.print_exc()
				if "poe" in s["updated"]:
					try:
						mention = s["notifications"]["tridolon"] if "tridolon" in s["notifications"] else None
						await wf.plains(client, wfinfo, handler, key, s["updated"]["poe"], mention)
					except discord.NotFound as e:
						del s["updated"]["poe"]
						print("msg removed poe")
					except Exception as e:
						print(e)
						traceback.print_exc()
				if "invasions" in s["updated"]:
					try:
						await wf.invasions(client, wfinfo, handler, helper, key, s["updated"]["invasions"])
					except discord.NotFound as e:
						del s["updated"]["invasions"]
						print("msg removed inv")
					except Exception as e:
						print(e)
						traceback.print_exc()
				if "fissures" in s["updated"]:
					try:
						await wf.fissures(client, wfinfo, handler, helper, key, s["updated"]["fissures"])
					except discord.NotFound as e:
						del s["updated"]["fissures"]
						print("msg removed fis")
					except Exception as e:
						print(e)
						traceback.print_exc()