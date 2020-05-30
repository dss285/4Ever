import asyncio
import json
import aiohttp
import re
import os
from bs4 import BeautifulSoup
class droptables:
	def __init__(self,):
		self.script_dir = "/home/dss/data/"
		self.droptables = {}
		self.loadTable()
	def requestKeys(self,request):
		if request in self.droptables.keys():
			return self.droptables[request].keys()
		else:
			print(self.droptables.keys())
			return None
	def requestTable(self,request,req2):
		drptbl = self.droptables[request][req2]
		return drptbl
	def loadTable(self,):
		with open(self.script_dir+'droptables.json') as f:
			self.droptables = json.load(f)

