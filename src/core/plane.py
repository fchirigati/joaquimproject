from util import *

import numpy

class Plane(object):
	"""
	Class that defines a plane.
	"""
	
	def __init__(self, point, vector):
		"""
		Constructor.
		It creates a plane based on a normal vector and a point.
		"""
		
		assert((len(point) == 4) and (len(vector) == 4))
		
		self.point = point
		self.perpVector = vector
		
		if self.perpVector[Z] != 0:
			self.perpVector[X] /= self.perpVector[Z]
			self.perpVector[Y] /= self.perpVector[Z]
			self.perpVector[Z] = 1
		
	def getZ(self, x, y):
		"""
		Given the X and Y coordinates of a point, returns the Z coordinate that is in the plane.
		"""
		
		if self.perpVector[Z] == 0:
			return self.point[Z]
		
		return self.point[Z] + self.perpVector[X]*(self.point[X]-x) + self.perpVector[Y]*(self.point[Y]-y)
	
	def contains(self, point):
		"""
		Returns True if the given point belongs to the plane, and False otherwise.
		"""
		
		assert(len(point) == 4)
		
		return abs(numpy.dot(self.perpVector, (self.point - point))) < 0.0001