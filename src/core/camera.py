from OpenGL.GL import *
from OpenGL.GLU import *

from util import *

import numpy

class Camera(object):
	"""
	This class represents the camera system.
	"""
	
	# Camera and perspective constants.
	POSITION = [0.0, 0.0, 3.0, 1]
	UPVECTOR = [0.0, 1.0, 0.0, 0]
	POINTER = [0.0, 0.0, -1.0, 0]
	LEFT_VECTOR = [-1.0, 0.0, 0.0, 0]
	FOVY = 45
	
	def __init__(self):
		"""
		Constructor.
		""" 
		
		# Camera's absolute position in world coordinates.
		self.position = numpy.array(Camera.POSITION)
		
		# Camera's up vector. Should always be unitary.
		self.upVector = numpy.array(Camera.UPVECTOR)
		
		# Vector that points to the direction that the camera is looking. Always unitary.
		self.pointer = numpy.array(Camera.POINTER)
		
		# Unitary vector perpendicular to the upVecor and the pointer, pointing to the left of the camera. 
		self.leftVector = numpy.array(Camera.LEFT_VECTOR)
		
		# Near/far clipping plane values.
		self.near, self.far = 1, 21
		
		# Width/height aspect of the view.
		self.aspect = 1
		
		# Overall rotation applied to the camera.
		self.rotation = numpy.identity(4)
		
		# Perspective angle (in degrees).
		self.fovAngle = Camera.FOVY
		
	def setView(self):
		"""
		Sets the camera to the current lookAt position and rotation angle.
		Warning: This method sets the matrix mode to GL_MODELVIEW.
		"""
		
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		
		gluLookAt(self.position[X], self.position[Y], self.position[Z],
				  self.position[X] + self.pointer[X], self.position[Y] + self.pointer[Y],
				  self.position[Z] + self.pointer[Z], self.upVector[X],
				  self.upVector[Y], self.upVector[Z])
		
	def setLens(self, width=None, height=None):
		"""
		Sets the lens of the camera.
		"""
		
		if width != None and height != None:
			self.aspect = float(width)/height
		
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(self.fovAngle, self.aspect, self.near, self.far)
		
	def getScenePosition(self, x, y):
		"""
		Gets the coordinates of the mouse in the scene, on the plane that is on the middle of the far and near planes.
		"""

		realFar = self.far
		self.far = (self.far - self.near) / 2
		self.setLens()
		coordPosition = gluUnProject(x, y, 1)
		self.far = realFar
		self.setLens()
		
		return arrayToVector(coordPosition, 1)
		
	def reset(self):
		"""
		Resets the camera system.
		"""
		
		self.position = numpy.array(Camera.POSITION)
		self.upVector = numpy.array(Camera.UPVECTOR)
		self.pointer = numpy.array(Camera.POINTER)
		self.leftVector = numpy.array(Camera.LEFT_VECTOR)
		self.rotation = numpy.identity(4)
		self.resetFovy()
		
	def resetFovy(self):
		"""
		Resets the fovy angle of the perspective.
		"""
		
		self.fovAngle = Camera.FOVY
		
	def rotate(self, rotation):
		"""
		Rotates the camera around the rotation center, given a rotation matrix.
		"""
		
		rotCenter = (self.position + self.pointer*(self.far-self.near)/2)[:3]
			
		glPushMatrix()
		glLoadIdentity()
		glTranslate(*rotCenter)
		glMultMatrixd(rotation)
		glTranslate(*-rotCenter)
		self.position = multiplyByMatrix(self.position)
		self.upVector = multiplyByMatrix(self.upVector)
		self.pointer = multiplyByMatrix(self.pointer)
		self.leftVector = multiplyByMatrix(self.leftVector)
		self.rotation = matrixByMatrix(rotation, self.rotation)
		glPopMatrix()
		
	def moveUp(self):
		"""
		Moves the camera up.
		"""
		
		self.position += self.upVector*0.1
	
	def moveDown(self):
		"""
		Moves the camera down.
		"""
		
		self.position -= self.upVector*0.1
	
	def moveLeft(self):
		"""
		Moves the camera to the left.
		"""
		
		self.position += self.leftVector*0.1
	
	def moveRight(self):
		"""
		Moves the camera to the right.
		"""
		
		self.position -= self.leftVector*0.1
	
	def moveForward(self):
		"""
		Moves the camera forward.
		"""
		
		self.position += self.pointer*0.1
	
	def moveBackward(self):
		"""
		Moves the camera backward.
		"""
		
		self.position -= self.pointer*0.1
		
	def tiltUp(self):
		"""
		Tilts the camera up.
		"""
		
		pass
	
	def tiltDown(self):
		"""
		Tilts the camera down.
		"""
		
		pass
	
	def tiltLeft(self):
		"""
		Tilts the camera left.
		"""
		
		pass
	
	def tiltRight(self):
		"""
		Tilts the camera right.
		"""
		
		pass