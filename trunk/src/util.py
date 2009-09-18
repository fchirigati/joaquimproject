X = 0
Y = 1
Z = 2
W = 3

def crossProduct(a, b):
	assert(len(a) == 3 and len(b) == 3)
	
	retVec = [0, 0, 0]
	retVec[X] = a[Y]*b[Z] - a[Z]*b[Y]
	retVec[Y] = a[Z]*b[X] - a[X]*b[Z]
	retVec[Z] = a[X]*b[Y] - a[Y]*b[X]
	
	return retVec

