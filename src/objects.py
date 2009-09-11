from OpenGL.GL import *
from OpenGL.raw.GLUT import *

class BaseObject(object):
	"""Base class for any object used in the GLWidget class."""
	def __init__(self):
		"""Constructor of the base class. Usually, it should be called in the constructor of the inherited classes."""
		self.rotationMatrix = []
		self.centralPos = []
		
	def render(self):
		"""Virtual method that must be overridden in base-classes."""
		pass
	
	def getRotationMatrix(self):
		return self.rotationMatrix
			
	def setRotationMatrix(self, rotationMatrix):
		self.rotationMatrix = rotationMatrix
		
	def getCentralPosition(self):
		return self.centralPos
			
	def setCentralPosition(self, centralPosition):
		self.centralPos = centralPosition

class Cube(BaseObject):
	"""Class that defines a cube."""
	
	def __init__(self, side, wire=True):
		"""Constructor."""
		
		super(Cube, self).__init__()
		self.side = side
		self.wire = wire
			
	def render(self):
		glTranslate(self.centralPos[0], self.centralPos[1], self.centralPos[2])
		if self.wire:
			glutWireCube(self.side)
		else:
			glutSolidCube(self.side)
			
class Sphere(BaseObject):
	"""Class that defines a sphere."""
	
	def __init__(self, radius, wire=True):
		"""Constructor."""
		super(Sphere, self).__init__()
		self.radius = radius
		self.wire = wire
		
	def render(self):
		glTranslate(self.centralPos[0], self.centralPos[1], self.centralPos[2])
		if self.wire:
			glutWireSphere(self.radius, 20, 20)
		else:
			glutSolidSphere(self.radius, 20, 20)
			