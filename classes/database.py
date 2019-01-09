import MySQLdb
class Database:
	def __init__(self,host,user,passwd,dbn):
		self.conn = self.conn(host, user, passwd, dbn)
		self.keywords = ["tridolon","nitain","helmet","forma","reactor","catalyst"]
		self.dicts = {}
		self.updateDict()
	def addBind(self,keyword,roleid,serverid):
		if keyword in self.keywords:
			args = ""
			c = self.conn.cursor()
			if not self.findIfBind(keyword,serverid):
				sql = "INSERT INTO binds VALUES (%s,%s,%s)"
				args = (keyword,roleid,serverid)
				c.execute(sql,args)
				self.conn.commit()
				c.close()
				
				return True
			else:
				self.updateBind(keyword,roleid,serverid,c)
		else:
			return False
	def updateBind(self,keyword,roleid,serverid, c):
		sql = "UPDATE binds SET role=%s WHERE serverid=%s AND type=%s"
		args = (roleid,serverid,keyword)
		c.execute(sql,args)
		self.conn.commit()
		c.close()
	def removeBind(self,keyword,serverid):
		if keyword in self.keywords:
			self.delete("DELETE FROM binds WHERE type=%s AND serverid=%s",(keyword,serverid))
			return True
		else:
			return False
	def findIfBind(self,keyword,serverid):
		c = self.conn.cursor()
		sql = "SELECT COUNT(*) FROM binds WHERE serverid=%s AND type=%s"
		c.execute(sql,(serverid,keyword))
		if c.fetchone()[0] > 0:
			return True
		else:
			return False
	def updateDict(self,):
		c = self.conn.cursor()
		nsfwchannels = {}
		c.execute("""SELECT * FROM nsfwchannels""")
		for row in c.fetchall():
			if row[1] in nsfwchannels.keys():
				nsfwchannels[row[1]].append(row[0])
			else:
				nsfwchannels[row[1]] = []
				nsfwchannels[row[1]].append(row[0])

		c.close()
		c = self.conn.cursor()
		c.execute("""SELECT * FROM server""")
		adminrid = {}
		for row in c.fetchall():
			adminrid[row[1]] = row[0]
		c.close()
		c = self.conn.cursor()
		alertmsgs = {}
		c.execute("""SELECT * FROM alertmessages""")
		for row in c.fetchall():
			if row[1] in alertmsgs.keys():
				alertmsgs[row[1]].append([row[0],row[2],row[3]])
			else:
				alertmsgs[row[1]] = []
				alertmsgs[row[1]].append([row[0],row[2],row[3]])
		c.close()
		c = self.conn.cursor()
		binds = {}
		c.execute("""SELECT * FROM binds""")
		for row in c.fetchall():
			if row[2] in binds.keys():
				binds[row[2]][row[0]] = row[1]
			else:
				binds[row[2]] = {}
				binds[row[2]][row[0]] = row[1]
		c.close()
		for key in adminrid.keys():
			self.dicts[key] = {}
			self.dicts[key]["adminrid"] = ""
			self.dicts[key]["alertmsgs"] = ""
			self.dicts[key]["binds"] = {}
			self.dicts[key]["nsfwchannels"] = []
			for key1,value in nsfwchannels.items():
				if key1==key:
					self.dicts[key]["nsfwchannels"] = value
			for key1,value in adminrid.items():
				if key1==key:
					self.dicts[key]["adminrid"] = value
			for key1,value in alertmsgs.items():
				if key1==key:
					self.dicts[key]["alertmsgs"] = value
			for key1,value in binds.items():
				if key1==key:
					self.dicts[key]["binds"] = value
	def conn(self, host, user, passwd, dbn):
		conn = MySQLdb.connect(host=host,user=user,passwd=passwd,db=dbn)
		return conn
	def insert(self, sql,args):
		c = self.conn.cursor()
		c.execute(sql,args)
		self.conn.commit()
		c.close()
	def delete(self, sql,args):
		c = self.conn.cursor()
		c.execute(sql,args)
		self.conn.commit()
		c.close()