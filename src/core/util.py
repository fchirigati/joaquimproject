from OpenGL.GL import *
from math import sqrt, acos, pi, degrees
import numpy

# Joaquim constants.
X = 0
Y = 1
Z = 2
W = 3

class Plane(object):
	"""
	Class that defines a plane.
	"""
	
	def __init__(self, vector, point):
		"""
		Constructor.
		It creates a plane based on a normal vector and a point.
		"""
		
		# Constants.
		self.A = 0.0
		self.B = 0.0
		self.C = 0.0
		self.D = 0.0
		
		assert((len(point) == 4) and (len(vector) == 4))
		
		self.A = vector[0]
		self.B = vector[1]
		self.C = vector[2]
		
		self.D = -((self.A*point[0]) + (self.B*point[1]) + (self.C*point[2]))
		
	def containsPoint(self, point):
		"""
		Returns True if point belongs to the plane, and False otherwise.
		"""
		
		assert(len(point) == 4)
		
		D_point = -((self.A*point[0]) + (self.B*point[1]) + (self.C*point[2]))
		print "D_point:", D_point
		
		if abs(D_point - self.D) < 0.0001:
			return True
		else:
			return False

def crossProduct(a, b):
	"""
	Returns the cross product between two 3-component vectors.
	"""
	
	assert(len(a) == 3 and len(b) == 3) or (len(a) == 4 and len(b) == 4)
	
	retVec = numpy.zeros(4)
	retVec[X] = a[Y]*b[Z] - a[Z]*b[Y]
	retVec[Y] = a[Z]*b[X] - a[X]*b[Z]
	retVec[Z] = a[X]*b[Y] - a[Y]*b[X]
	retVec[W] = 0
	
	return retVec

def multiplyByMatrix(vector):
	"""
	Multiplies a given vector by the current matrix on the current
	GLMatrixMode stack, then returns the result.
	"""
	
	assert(len(vector) == 4)
	
	glMode = glGetInteger(GL_MATRIX_MODE)
	assert(glMode == GL_MODELVIEW or glMode == GL_PROJECTION)
	
	vecMatrix = numpy.zeros(16)
	for i in range(4):	
		vecMatrix[i] = vector[i]
	
	glPushMatrix()
	glMultMatrixd(vecMatrix)
	if glMode == GL_MODELVIEW:
		retVec = glGetDouble(GL_MODELVIEW_MATRIX)[0]
	elif glMode == GL_PROJECTION:
		retVec = glGetDouble(GL_PROJECTION_MATRIX)[0]
	else:
		retVec = numpy.zeros(4)
	glPopMatrix()
	
	# Normalize the vector, if it's a point.
	if (retVec[W] != 0):
		retVec /= retVec[W]
	
	return numpy.array(retVec)

def matrixByMatrix(a, b):
	"""
	Multiplies two matrices (a x b) and returns the result.
	"""
	
	glMode = glGetInteger(GL_MATRIX_MODE)
	assert(glMode == GL_MODELVIEW or glMode == GL_PROJECTION)
	
	glPushMatrix()
	glLoadMatrixd(a)
	glMultMatrixd(b)
	if glMode == GL_MODELVIEW:
		retMatrix = glGetDouble(GL_MODELVIEW_MATRIX)
	elif glMode == GL_PROJECTION:
		retMatrix = glGetDouble(GL_PROJECTION_MATRIX)
	glPopMatrix()
	
	return retMatrix

def distance(a, b):
	"""
	Returns the distance between two vectors/points.
	"""
	
	assert(len(a) == len(b))
	
	sum = 0
	for i in range(len(a)):
		sum += (a[i] - b[i]) * (a[i] - b[i])
	
	return sqrt(sum)

def angle(a, b):
	"""
	Returns the angle between two vectors in degrees.
	"""
	
	assert(len(a) == len(b))
	
	return degrees(acos(numpy.dot(a, b) / (lengthVector(a) * lengthVector(b))))

def lengthVector(a):
	"""
	Returns the length of a given vector.
	"""
	
	sum = 0
	for i in range(len(a)):
		sum += a[i]*a[i]
		
	return sqrt(sum)

def arrayToVector(array, newElement=None):
	"""
	Returns the numpy representation of a vector given an array.
	Optionally, adds an element to the end of the array.
	"""
	
	length = len(array)
	if newElement != None:
		length += 1
		
	retVec = numpy.zeros(length)
	for i in range(len(array)):
		retVec[i] = array[i]
		
	if newElement != None:
		retVec[length-1] = newElement
	
	return retVec

def vector(point_1, point_2):
	"""
	Returns the vector between two given points.
	Note that point_2 is the destination point.
	"""
	
	assert((len(point_1) == 4) and (len(point_2) == 4))
	
	vector = numpy.zeros(4)
	for i in range(3):
		vector[i] = point_2[i] - point_1[i]
	
	return vector

def applyVector(point, vector):
	"""
	Apply a shift (vector) to point, returning the new point.
	"""
	
	assert((len(point) == 4) and (len(vector) == 4))
	
	new_point = numpy.zeros(4)
	for i in range(3):
		new_point[i] = point[i] + vector[i]
	
	return new_point