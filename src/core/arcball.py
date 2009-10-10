from OpenGL.GL import *
from OpenGL.GLU import *
from math import *
import numpy

from util import *

class ArcBall(object):
	"""
	This class represents an arcball object.
	"""
	
	def __init__(self, parent):
		"""
		Default constructor.
		"""
		
		# Absolute position of the arcball in the scene.
		self.centralPos = [0.0, 0.0, 0.0]
		# Real radius of the arcball's sphere.
		self.radius = 0.0
		# Initial point clicked, in the sphere's coordinates, before dragging the arcball.
		self.initialPt = [0, 0, 0]
		# Final point on the sphere that should be used to determine the arcball rotation.
		self.finalPt = [0, 0, 0]
		# Set a reference to the GLWidget that contains this ArcBall object.
		self.parent = parent
		
	def setCentralPosition(self, newPosition):
		self.centralPos = newPosition
		
	def setRadius(self, newRadius):
		self.radius = newRadius
		
	def setInitialPt(self, x, y):
		"""
		Sets the initial point of the arcball manipulation, in screen coordinates.
		"""
		
		self.initialPt = self.screenToSphereCoordinates(x, y)
		
	def setFinalPt(self, x, y, inverse=False):
		"""
		Sets the final point of the arcball manipulation, in screen coordinates,
		returning the rotation matrix associated with the movement.
		"""
		
		self.finalPt = self.screenToSphereCoordinates(x, y)
		retMatrix = self.__getRotation()
		self.initialPt = self.finalPt
		
		if inverse:
			retMatrix = numpy.transpose(retMatrix)
		
		return retMatrix  
		
	def screenToSphereCoordinates(self, x, y):
		"""
		Maps screen coordinates to the arcball's sphere coordinates.
		Warning: This method sets the matrix mode to GL_MODELVIEW.
		"""
		
		# Initialize sphere coordinates array (return value).
		sphereCoords = numpy.zeros(4)
		sphereCoords[W] = 1
		
		# Gets the sphere's center position on the screen.
		screenCenter = gluProject(self.centralPos[X], self.centralPos[Y], self.centralPos[Z])[:2]
		
		# Calculates the radius of the sphere projected on the screen.
		viewport = glGetInteger(GL_VIEWPORT)
		screenBorder = [None, None]
		perpVector = numpy.array(self.parent.upVector) * self.radius
		
		glMatrixMode(GL_MODELVIEW)
		borderPoint = multiplyByMatrix(self.centralPos) + perpVector
		glMatrixMode(GL_PROJECTION)
		projectionPoint = multiplyByMatrix(borderPoint)
		screenBorder[X] = viewport[0] + viewport[2] * (projectionPoint[0]*0.5 + 0.5)
		screenBorder[Y] = viewport[1] + viewport[3] * (projectionPoint[1]*0.5 + 0.5)
		screenRadius = distance(screenCenter, screenBorder)
		
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
			
		# Rotates the sphere coordinates according to the camera.
		glMatrixMode(GL_MODELVIEW)
		glPushMatrix()
		# Unsets all translations in the matrix.
		tempMatrix = glGetDouble(GL_MODELVIEW_MATRIX)
		for i in range(3):
			tempMatrix[W][i] = 0
		# Makes the inverse rotation to the coordinates (we have the camera's rotation).
		glLoadMatrixd(numpy.transpose(tempMatrix))
		sphereCoords = multiplyByMatrix(sphereCoords)
		glPopMatrix()
			
		return sphereCoords
	
	def __getRotation(self):
		"""
		Returns the rotation matrix of the arcball based on the initial and final points.
		Warning: This method sets the matrix mode to GL_MODELVIEW.
		"""
		
		glMatrixMode(GL_MODELVIEW)
		
		perpVector = crossProduct(self.initialPt, self.finalPt)
		
		glPushMatrix()
		glLoadIdentity()
		glRotate(angle(self.initialPt, self.finalPt), *perpVector[:3])
		retMatrix = glGetDouble(GL_MODELVIEW_MATRIX)
		glPopMatrix()
		
		return retMatrix

class SceneArcBall(ArcBall):
	"""
	Specific ArcBall object for the overall scene.
	"""
	
	#def __init__(self, parent):
	#	super(SceneArcBall, self).__init__(parent)
	
	def screenToSphereCoordinates(self, x, y):
		"""
		Maps screen coordinates to the arcball's sphere coordinates.
		Warning: This method sets the matrix mode to GL_MODELVIEW.
		"""
		
		# Initialize sphere coordinates array (return value).
		sphereCoords = numpy.zeros(4)
		sphereCoords[W] = 1
		
		# Gets the sphere's center position on the screen.
		screenCenter = [self.parent.wWidth*0.5, self.parent.wHeight*0.5]
		
		# Calculates the radius of the sphere projected on the screen.
		screenRadius = lengthVector(screenCenter)
		
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
			
		# Rotates the sphere coordinates according to the camera.
		glMatrixMode(GL_MODELVIEW)
		glPushMatrix()
		# Unsets all translations in the matrix.
		tempMatrix = glGetDouble(GL_MODELVIEW_MATRIX)
		for i in range(3):
			tempMatrix[W][i] = 0
		# Makes the inverse rotation to the coordinates (we have the camera's rotation).
		glLoadMatrixd(numpy.transpose(tempMatrix))
		sphereCoords = multiplyByMatrix(sphereCoords)
		glPopMatrix()
			
		return sphereCoords