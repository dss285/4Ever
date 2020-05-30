import re
import math
class mathBot:
	def probability(self, message,key):
		tags = message[len(key+'probability'):].strip()
		reg = re.match(key+"probability\s(\d+)\s(\d+)\s([\d\.\/]+)", message)
		if reg:
			chance = 0
			if '/'  in reg.group(3):
				chance = self.convertDivToFloat(reg.group(3))
			else:
				chance = float(reg.group(3))
			msg = str(self.probabilitymath(reg.group(1),reg.group(2),chance)*100)+" [%]\n"
			var = 0
			for i in range(int(reg.group(1))):
				save = self.probabilitymath(reg.group(1),i,chance)
				var = var+save
			var = 1 - var
			msg = "> Probability of exact: "+msg
			msg = msg + "> Probability of atleast number: "+str(var*100)+" [%]"
			return msg
	def convertDivToFloat(self, div):
		splitted = div.split("/")
		if splitted[0] != 0:
			return float(splitted[0])/float(splitted[1])
	def probabilitymath(self,trials, drops, chance):
		coefficient = self.coefficient(int(trials),int(drops))
		powprobability = chance**int(drops)
		powprobability2 = (1-float(chance))**(int(trials)-int(drops))
		probabilityout = coefficient*powprobability*powprobability2
		return probabilityout

	def coefficient(self,trials, successes):
		if(successes > trials - successes):
			successes = trials-successes
		res = 1
		for i in range(successes): 
			res = res * (trials - i) 
			res = res / (i + 1) 
		return res
	
	def pythagoras(self, a=None, b=None, c=None):
		#c = a + b
		#b = c - a
		#a = c - b
		if a and b: 
			return math.sqrt(math.pow(a,2)+math.pow(b,2))
		elif c and a:
			return math.sqrt(math.pow(c,2)-math.pow(a,2))
		elif c and b:
			return math.sqrt(math.pow(c,2)-math.pow(b,2))
		return None

	def damageReduction(self,armor):
		print(armor)
		return armor/(armor+300)

	def effectiveHPArmor(self,armor,hp):
		return hp/(1-self.damageReduction(armor))
	def effectiveHPReduction(self,reduction,hp):
		return hp/(1-reduction)
	def frostGlobe(self,armorMultiplier, abilitystr,armor):
		return (5000+5*(armor+300)*armorMultiplier)*(1+abilitystr)
	def garaBlade(self,damage,elements,extrastr):
		return 800*(1+float(damage))*(1+float(elements))*(1+float(extrastr))
