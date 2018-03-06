import MySQLdb
class Database:
	def __init__(self,host,user,passwd,dbn):
		self.conn = self.conn(host, user, passwd, dbn)
		self.adminRole = []
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
	def updateDics(self,which):
		c = self.conn.cursor()
		if which.startswith('server'):
			c.execute("""SELECT * FROM server""");
			for row in c.fetchall():
				self.adminRole.append([row[1],row[2]])
			else:
				return self.adminRole
