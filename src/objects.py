from OpenGL.GL import *
from OpenGL.raw.GLUT import *
from arcball import *
from util import *

class BaseObject(object):
	"""Base class for any object used in the GLWidget class."""
	
	def __init__(self):
		"""Constructor of the base class. Usually, it should be called in the constructor of the inherited classes."""
		
		self.rotationMatrix = []
		self.centralPos = []
		self.selected = False
		
		self.r = 1.0
		self.g = 0.0
		self.b = 0.0
			
	def render(self):
		"""Virtual method that should be overridden in base-classes."""
		pass
	
	def changeColor(self):
		if [self.r, self.g] == [1.0, 0.0]:
			self.r = 0.0
			self.g = 1.0
		else:
			self.r = 1.0
			self.g = 0.0
			
	def selectionStatus(self):
		return self.selected
			
	def selectObject(self):
		self.selected = not(self.selected)
		self.changeColor()
	
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
		
	def render(self, translation=True):
		if translation:
			glColor3f(self.r, self.g, self.b)
			glTranslate(self.centralPos[X], self.centralPos[Y], self.centralPos[Z])
			glMultMatrixf(self.rotationMatrix)
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
		
	def render(self, translation=True):
		if translation:
			glColor3f(self.r, self.g, self.b)
			glTranslate(self.centralPos[X], self.centralPos[Y], self.centralPos[Z])
			glMultMatrixf(self.rotationMatrix)
		if self.wire:
			glutWireSphere(self.radius, 20, 20)
		else:
			glutSolidSphere(self.radius, 20, 20)
		
