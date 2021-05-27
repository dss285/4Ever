import numpy as np
import matplotlib.pyplot as plt
import math
def equationGraph(formula, x_range, tick_n):
	x = np.array(x_range)
	y = eval(formula)
	plt.plot(x, y)
	plt.xticks(np.arange(min(x), max(x)+1, tick_n))
	plt.grid(True)
	plt.savefig('test.png')
def base2_to_base10(binary):
	potency = len(binary)-1
	total = 0
	for i in binary:
		total += (int(i)*2)**potency
		potency -=1
	return total
def base10_to_base2(decimal):
	potency = math.ceil(math.log(decimal, 2))
	potency_tmp = potency
	total = decimal
	tmp = ""
	while total != 0:
		iteration = 2**potency
		if total-iteration >= 0:
			tmp += "1"
			total -= iteration
		else:
			tmp += "0"
		potency -= 1
	while len(tmp) < potency_tmp+1:
		tmp += "0"
	if tmp[0] == "0":
		tmp = tmp[1:]
	return tmp
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
	coeff = coefficient(int(trials),int(drops))
	pow_probability = chance**int(drops)
	pow_probability_2 = (1-float(chance))**(int(trials)-int(drops))
	probability_out = coeff*pow_probability*pow_probability_2
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
if __name__ == "__main__":
	print(base2_to_base10("100000000001"))
	print(base10_to_base2(2049))