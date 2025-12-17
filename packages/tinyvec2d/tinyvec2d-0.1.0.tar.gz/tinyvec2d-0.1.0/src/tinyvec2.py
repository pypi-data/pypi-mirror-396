import math
vec = tuple[float, float]
epsilon = 10**(-9)
def check(u, v):
	if len(u) != len(v):
		raise TypeError
	if len(u) != 2:
		raise TypeError
def distance(u: vec, v: vec) -> float:
	check(u, v)
	ux, uy = u
	vx, vy = v
	res = math.sqrt((vx-ux)**2 + (vy-uy)**2)
	return(res)
def length(w: vec) -> float:
	if len(w) != 2:
		raise TypeError
	x, y = w
	res = math.sqrt(x**2 + y**2)
	return(res)
def dot(u: vec, v: vec) -> float:
	check(u, v)
	ux, uy = u
	vx, vy = v
	res = (ux * vx) + (uy * vy)
	return(res)
def normalize(w: vec) -> vec:
	if len(w) != 2:
		raise TypeError
	x, y = w
	lengtth = length((x, y))
	if abs(lengtth) < epsilon:
		raise
	res = (x/lengtth, y/lengtth)
	return(res)
def add(u: vec, v: vec) -> vec:
	check(u, v)
	ux, uy = u
	vx, vy = v
	w = (ux+vx, uy+vy)
	return(w)
def sub(u: vec, v: vec) -> vec:
	check(u, v)
	ux, uy = u
	vx, vy = v
	w = (ux-vx, uy-vy)
	return(w)
def scalar_mul(w: vec, a: float) -> vec:
	if len(w) != 2:
		raise TypeError
	x, y = w
	res = (x*a, y*a)
	return(res)
def scalar_div(w: vec, a: float) -> vec:
	if len(w) != 2:
		raise TypeError
	if abs(a) < epsilon:
		raise ZeroDivisionError
	x, y = w
	res = (x/a, y/a)
	return(res)