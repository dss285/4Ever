import urllib
import urllib.request
import classes
class Utilities:
	def __init__(self,):
		self.voiceplayers = []
		
	def CommandPreTest(self,message,command,key='!'):
		if message.content.startswith(key+command):
			return True
		else:
			return False
	def openImgUrl(self, url,file='temp.png'):
		hdr = {'User-Agent':'Mozilla/5.0','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
		req = urllib.request.Request(url, headers=hdr)
		with urllib.request.urlopen(req) as url:
			with open(file,'wb') as f:
				f.write(url.read())
		img = Image.open(file)
		return img
	def addVoicePlayer(self,voiceplayer):
		self.voiceplayers.append(voiceplayer)