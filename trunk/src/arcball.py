from OpenGL.GL import *
from OpenGL.GLU import *
from math import *
import numpy

from util import *

class ArcBall(object):
	"""This class represents an arcball object."""
	
	def __init__(self):
		"""Default constructor."""
		
		# Absolute position of the arcball in the scene.
		self.centralPos = [0.0, 0.0, 0.0]
		# Real radius of the arcball's sphere.
		self.radius = 0.0
		# Initial point clicked, in the sphere's coordinates, before dragging the arcball.
		self.initialPt = [0, 0, 0]
		# Final point on the sphere that should be used to determine the arcball rotation.
		self.finalPt = [0, 0, 0]
		
	def setCentralPosition(self, newPosition):
		self.centralPos = newPosition
		
	def setRadius(self, newRadius):
		self.radius = newRadius
		
	def setInitialPt(self, x, y):
		"""Sets the initial point of the arcball manipulation, in screen coordinates."""
		
		self.initialPt = self.screenToSphereCoordinates(x, y)
		
	def setFinalPt(self, x, y):
		"""Sets the final point of the arcball manipulation, in screen coordinates,
		returning the rotation matrix associated with the movement.
		This method does not unset the initial point."""
		
		self.finalPt = self.screenToSphereCoordinates(x, y)
		
		quaternion = crossProduct(self.initialPt, self.finalPt)
		quaternion.append(numpy.dot(self.initialPt, self.finalPt))
		
		retMatrix = numpy.matrix(self.__getRotationMatrix(quaternion))
		
		self.initialPt = self.finalPt
		
		return retMatrix  
		
	def screenToSphereCoordinates(self, x, y):
		"""Maps screen coordinates to the arcball's sphere coordinates."""
		
		# Initialize sphere coordinates array (return value).
		sphereCoords = [0, 0, 0]
		
		# Gets the sphere's center position on the screen.
		screenCenter = gluProject(self.centralPos[X], self.centralPos[Y], self.centralPos[Z])
		#screenCenter = gluProject(self.centralPos[X], self.centralPos[Y], self.centralPos[Z],
		#						glGetDoublev(GL_MODELVIEW_MATRIX),
		#						glGetDoublev(GL_PROJECTION_MATRIX))
		
		# Calculates the radius of the sphere projected on the screen.
		_Z = 1
		d = 1.0
		#screenRadius = self.radius * _Z * d * glGetIntegerv(GL_VIEWPORT)[2]
		screenRadius = self.radius * _Z / d * 0.5 * glGetIntegerv(GL_VIEWPORT)[2]
		print screenRadius
		
		# Finally, sets the sphere coordinates.
		sphereCoords[X] = (x - screenCenter[X]) / screenRadius
		sphereCoords[Y] = (y - screenCenter[Y]) / screenRadius 
		r = sphereCoords[X]*sphereCoords[X] + sphereCoords[Y]*sphereCoords[Y]
		if (r > 1):
			# Selected point is outside the sphere boudings on the screen.
			sphereCoords[X] /= sqrt(r)
			sphereCoords[Y] /= sqrt(r)
		else:
			sphereCoords[Z] = sqrt(1 - r)
			
		print sphereCoords
		
		return sphereCoords
	
	def __getRotationMatrix(self, q):
		"""Transforms a quaternion into a rotation matrix and returns it."""
		
		assert(len(q) == 4)
		
		n = 0
		for i in range(4):
			n += q[i]*q[i]

		s = 0.0
		if (n > 0.0):
			s = 2.0 / n
		
		xs = q [X] * s
		ys = q [Y] * s
		zs = q [Z] * s
		wx = q [W] * xs
		wy = q [W] * ys
		wz = q [W] * zs
		xx = q [X] * xs
		xy = q [X] * ys
		xz = q [X] * zs
		yy = q [Y] * ys
		yz = q [Y] * zs
		zz = q [Z] * zs

		# See Lengyel pages 88-92
		rot = [	[1.0 - (yy + zz),	xy - wz,			xz + wy,			0],
				[xy + wz,			1.0 - (xx + zz),	yz - wx,			0],
				[xz - wy,			yz + wx,			1.0 - (xx + yy),	0],
				[0, 				0,					0,					1]] 
		
		return rot