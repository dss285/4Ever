import MySQLdb
import asyncio
import discord
import urllib
import urllib.request
from classes import database
from PIL import Image
class Main:
	def __init__(self,host,user,passwd,dbn):
		self.db = database.Database(host,user,passwd,dbn)
		self.conn = self.db.conn
		self.adminRole=[]
	def insertInto(self,adminrole):
		self.adminRole = adminrole
