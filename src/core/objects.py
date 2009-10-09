from OpenGL.GL import *
from OpenGL.raw.GLUT import *
from arcball import *
from util import *
from math import sqrt

class BaseObject(object):
	"""
	Base class for any object used in the GLWidget class.
	"""
	
	def __init__(self, parent):
		"""
		Constructor of the base class. Usually, it should be called in
		the constructor of the inherited classes.
		"""
		
		self.rotation = []
		self.centralPos = []
		
		# Radius of the bouding sphere that surrounds the object. 
		self.radius = 0.0
		self.selected = False
		self.rotating = False
		
		# Initial color of the object.
		self.r, self.g, self.b = 1.0, 0.0, 0.0
		
		# Reference to the GLWidget object that contains this object.
		self.parent = parent
		self.arcBall = ArcBall(self.parent)
			
	def render(self):
		"""
		Virtual method that should be overridden in base-classes.
		"""
		
		pass
			
	def isSelected(self):
		"""
		Indicates whether the object is selected or not.
		"""
		
		return self.selected
			
	def select(self, newStatus):
		"""
		Selects or unselects the object, depending on the newStatus argument.
		Also changes the object's color according to the selection status.
		"""
		
		self.selected = newStatus
		if self.selected:
			self.r, self.g, self.b = 0, 1, 0
		else:
			self.r, self.g, self.b = 1, 0, 0
			
	def rightClickEvent(self, x, y):
		"""
		"""
		
		self.rotating = True
		self.arcBall.setInitialPt(x, y)
	
	def rightClickMoveEvent(self, x, y):
		"""
		"""
		
		r = self.arcBall.setFinalPt(x, y)
		self.rotation = matrixByMatrix(r, self.rotation)
		
	def rightClickReleaseEvent(self, x, y):
		"""
		"""
		
		self.rotating = False
	
	def getRotationMatrix(self):
		"""
		Returns the rotation matrix.
		"""
		
		return self.rotation
		
	def setRotationMatrix(self, rotationMatrix):
		"""
		Defines a new rotation matrix.
		"""
		
		self.rotation = rotationMatrix
		
	def getCentralPosition(self):
		"""
		Returns the central position.
		"""
		
		return self.centralPos
		
	def setCentralPosition(self, centralPosition):
		"""
		Defines a new central position.
		"""
		
		self.centralPos = centralPosition
		self.arcBall.setCentralPosition(self.centralPos)
		
	def setRadius(self, newRadius):
		"""
		"""
		
		self.radius = newRadius
		self.arcBall.radius = self.radius

class Cube(BaseObject):
	"""
	Class that defines a cube.
	"""
	
	def __init__(self, side, parent, wire=True):
		"""
		Constructor.
		"""
		
		super(Cube, self).__init__(parent)
		self.side = side
		self.wire = wire
		self.setRadius(side * sqrt(3) / 2.0)
		
	def render(self):
		"""
		Renders the cube.
		"""
		
		glColor3f(self.r, self.g, self.b)
		glTranslate(self.centralPos[X], self.centralPos[Y], self.centralPos[Z])
		glMultMatrixf(self.rotation)
		if self.wire:
			glutWireCube(self.side)
		else:
			glutSolidCube(self.side)
			
		if self.rotating:
			glColor(0.3, 0.6, 1)
			glutWireSphere(self.radius + 0.005, 20, 20)
		
class Sphere(BaseObject):
	"""
	Class that defines a sphere.
	"""
	
	def __init__(self, radius, parent, wire=True):
		"""
		Constructor.
		"""
		
		super(Sphere, self).__init__(parent)
		self.wire = wire
		self.setRadius(radius)
		
	def render(self):
		"""
		Renders the sphere.
		"""
		
		glColor(self.r, self.g, self.b)
		glTranslate(self.centralPos[X], self.centralPos[Y], self.centralPos[Z])
		glMultMatrixf(self.rotation)
		
		if self.wire:
			glutWireSphere(self.radius, 20, 20)
		else:
			glutSolidSphere(self.radius, 20, 20)
			
		if self.rotating:
			glColor(0.3, 0.6, 1)
			glutWireSphere(self.radius + 0.005, 20, 20)
		
