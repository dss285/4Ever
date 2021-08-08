import numpy as np
import matplotlib.pyplot as plt
import math
def equationGraph(formula : str, x_range : int, tick_n):
	x = np.array(x_range)
	y = eval(formula)
	plt.plot(x, y)
	plt.xticks(np.arange(min(x), max(x)+1, tick_n))
	plt.grid(True)
	plt.savefig('test.png')

def commonOnotations():
	x = np.array(range(1, 12))
	y = [
		np.log(x),
		x,
		x*np.log(x),
		x**2,
		x**3,
		2**x,
		
	]
	labels = [
		"LOG N",
		"N",
		"N LOG N",
		"N^2",
		"N^3",
		"2^N"
	]
	for i, label in zip(y, labels):
		plt.plot(x, i, label=f"O({label})")
		
	plt.xticks(np.arange(min(x), max(x)+1, 10.0))
	plt.ylabel('Steps')
	plt.xlabel('Items')
	plt.grid(True)
	plt.legend()
	plt.savefig('onotation.png')
def probability(trials : int, successes : int, chance : float) -> float:
	coeff = coefficient(trials, successes)
	pow_probability = chance**successes
	pow_probability_2 = (1-chance)**(trials-successes)
	probability_out = coeff*pow_probability*pow_probability_2
	return probability_out
def coefficient(trials : int, successes : int) -> float:
	if(successes > trials - successes):
		successes = trials-successes
	res = 1
	for i in range(successes): 
		res = res * (trials - i) 
		res = res / (i + 1) 
	return res
def pythagoras(a=None, b=None, c=None) -> float:
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
	print(commonOnotations())