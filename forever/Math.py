import numpy as np
import matplotlib.pyplot as plt
import math
import numpy
class Math:
	def equationGraph(formula, x_range, tick_n):
		x = np.array(x_range)
		y = eval(formula)
		plt.plot(x, y)
		plt.xticks(np.arange(min(x), max(x)+1, tick_n))
		plt.grid(True)
		plt.savefig('test.png')
	def commonOnotations():
		x = np.array(range(1, 8))
		y = [
			np.log(x),
			x,
			x*np.log(x),
			x**2,
			x**3,
			2**x,
			
		]
		for i in y:
			print(i)
			plt.plot(x, i, label='O()')
			
		plt.xticks(np.arange(min(x), max(x)+1, 10.0))
		plt.ylabel('Steps')
		plt.xlabel('Items')
		plt.grid(True)
		plt.savefig('onotation.png')
	def probability(trials, drops, chance):
		coefficient = Math.coefficient(int(trials),int(drops))
		pow_probability = chance**int(drops)
		pow_probability_2 = (1-float(chance))**(int(trials)-int(drops))
		probability_out = coefficient*pow_probability*pow_probability_2
		return probability_out
	def coefficient(trials, successes):
		if(successes > trials - successes):
			successes = trials-successes
		res = 1
		for i in range(successes): 
			res = res * (trials - i) 
			res = res / (i + 1) 
		return res
	def pythagoras(a=None, b=None, c=None):
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
