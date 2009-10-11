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
		self._centralPos = []
		
		# Radius of the bouding sphere that surrounds the object. 
		self._radius = 0.0
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
		Method called when the object should be drawn.
		"""
		
		pass
			
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
		TO-DO
		"""
		
		self.rotating = True
		self.arcBall.setInitialPt(x, y)
	
	def rightClickMoveEvent(self, x, y):
		"""
		TO-DO
		"""
		
		r = self.arcBall.setFinalPt(x, y)
		self.rotation = matrixByMatrix(r, self.rotation)
		
	def rightClickReleaseEvent(self, x, y):
		"""
		TO-DO
		"""
		
		self.rotating = False
		
	@property
	def centralPosition(self):
		return self._centralPos
		
	@centralPosition.setter
	def centralPosition(self, value):
		self._centralPos = value
		self.arcBall.setCentralPosition(self._centralPos)
		
	@property
	def radius(self):
		return self._radius
		
	@radius.setter
	def radius(self, value):
		self._radius = value
		self.arcBall.radius = self._radius

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
		self.radius = side * sqrt(3) / 2.0
		
	def render(self):
		"""
		Renders the cube.
		"""
		
		glColor3f(self.r, self.g, self.b)
		glTranslate(*self._centralPos[:3])
		glMultMatrixf(self.rotation)
		
		if self.wire:
			glutWireCube(self.side)
		else:
			glutSolidCube(self.side)
			
		if self.rotating:
			glColor(0.3, 0.6, 1)
			glutWireSphere(self._radius + 0.005, 20, 20)
		
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
		self.radius = radius
		
	def render(self):
		"""
		Renders the sphere.
		"""
		
		glColor(self.r, self.g, self.b)
		glTranslate(*self._centralPos[:3])
		glMultMatrixf(self.rotation)
		
		if self.wire:
			glutWireSphere(self._radius, 20, 20)
		else:
			glutSolidSphere(self._radius, 20, 20)
			
		if self.rotating:
			glColor(0.3, 0.6, 1)
			glutWireSphere(self._radius + 0.005, 20, 20)
		
