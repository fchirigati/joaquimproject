from OpenGL.raw.GLUT import glutWireSphere, glutSolidSphere
from util import *
from arcball import *

import numpy

class Group(object):
	"""
	This class represents a group of objects.
	"""

	def __init__(self, parent):
		"""
		Creates a new Group object.
		"""
		
		# List of objects in this group.
		self._objects = []
		
		# Center position of the group, in world coordinates.
		self._centralPos = numpy.zeros(4)
		self._centralPos[W] = 1
		
		# Rotation of the group.
		self.rotation = numpy.identity(4)
		
		# Radius of the sphere that bounds all the objects in the group.
		self._radius = 0
		
		# Maximum distance between two objects in the group.
		self._maxDistance = 0
		
		# Reference to the GLWidget object that contains this object.
		self.arcBall = ArcBall(parent)
		
		# Indicates whether the object is rotatingScene or not.
		self.rotatingScene = False
		
		# Vector from the object's screen center to the point where it was clicked.
		self.fromCenter = numpy.zeros(2)
		
		# Maximum object size of all objects in this group.
		self.maxObjectSize = 0 
		
	def __iter__(self):
		"""
		Object that will have the iteration items.
		"""
		
		return self._objects.__iter__()
	
	def __len__(self):
		"""
		Returns how many objects there are in this group.
		"""
		
		return len(self._objects)
	
	def leftClickPressEvent(self, x, y):
		"""
		Method called when the left mouse button is pressed.
		"""
		
		screenPos = gluProject(*self._centralPos[:3])
		self.fromCenter = numpy.array([x, y]) - screenPos[:2]
	
	def leftClickMoveEvent(self, x, y):
		"""
		Method called when the mouse moves and the left mouse button is pressed.
		"""
		
		screenPos = gluProject(*self._centralPos[:3])
		shift = arrayToVector(gluUnProject(x - self.fromCenter[X], y - self.fromCenter[Y], screenPos[Z]), 1) - self._centralPos
		
		for obj in self._objects:
			obj.centralPosition += shift
		
		self._centralPos += shift
	
	def rightClickEvent(self, x, y):
		"""
		Method called when the right mouse button is pressed.
		"""
		
		if len(self._objects) == 0:
			return
		
		self.rotatingScene = True
		self.arcBall.setInitialPt(x, y)
	
	def rightClickMoveEvent(self, x, y):
		"""
		Method called when the mouse moves and the right mouse button is pressed.
		"""
		
		if len(self._objects) == 0:
			return
		
		r = self.arcBall.setFinalPt(x, y)
		self.rotation = matrixByMatrix(r, self.rotation)
		
		glPushMatrix()
		glLoadIdentity()
		glTranslate(*self._centralPos[:3])
		glMultMatrixd(r)
		glTranslate(*-self._centralPos[:3])
		for obj in self._objects:
			obj.centralPosition = multiplyByMatrix(obj.centralPosition)
			obj.rotation = matrixByMatrix(r, obj.rotation)
		glPopMatrix()
		
	def rightClickReleaseEvent(self, x, y):
		"""
		Method called when the left mouse button is released.
		"""
		
		if len(self._objects) == 0:
			return
		
		self.rotatingScene = False
	
	@property
	def centralPosition(self):
		"""
		Center position of the group, in world coordinates.
		"""
		
		return self._centralPos
	
	@centralPosition.setter
	def centralPosition(self, value):
		"""
		Sets the new central position of the group, shifting all the objects' central positions.
		"""
		
		shift = value - self._centralPos
		
		for obj in self._objects:
			obj.centralPosition += shift
			obj.arcBall.centralPos += shift
			
		self._centralPos += shift
		self.arcBall.centralPos += shift
	
	@property
	def radius(self):
		"""
		Radius of the sphere that bounds all the objects in the group.
		"""
		
		return self._radius
	
	def add(self, object, autoSelect=True):
		"""
		Adds an object to the group.
		"""
		
		newPts = None
		for obj in self._objects:
			dist = lengthVector(obj.centralPosition - object.centralPosition)
			if dist > self._maxDistance:
				newPts = [obj, object]
				self._maxDistance = dist
				
		if object.size > self.maxObjectSize:
			self.maxObjectSize = object.size
				
		self._objects.append(object)
		
		if autoSelect:
			object.select(True)
		
		if len(self._objects) == 1:
			self._radius = self._objects[0].radius
			self._centralPos = self._objects[0].centralPosition.copy()
			self.arcBall.centralPos = self._centralPos
			self.arcBall.radius = self._radius
			return
		
		# The group center remains the same.
		if newPts is None:
			dist = lengthVector(object.centralPosition - self._centralPos) + object.radius
			if self._radius < dist:
				self._radius = dist
				self.arcBall.radius = dist
			return
		
		# A new central position of the group is set.
		self._centralPos = (newPts[0].centralPosition + newPts[1].centralPosition) * 0.5
		self._radius = self._maxDistance * 0.5 + max(newPts[0].radius, newPts[1].radius)
		
		# Iterates over objects in the group to verify if there are any objects outside the current sphere.
		for obj in self._objects:
			dist = lengthVector(obj.centralPosition - self._centralPos) + obj.radius
			if dist > self._radius:
				self._radius = dist
		
		self.arcBall.centralPos = self._centralPos
		self.arcBall.radius = self._radius
		
	def remove(self, object, autoDeselect=True):
		"""
		Removes an object from the group.
		"""
		
		self._objects.remove(object)
		
		if autoDeselect:
			object.select(False)
		
		self.updateRadiusAndCenter()
		
	def removeAll(self):
		"""
		Removes all objects from the group.
		"""
		
		for obj in self._objects:
			obj.select(False)
			
		del self._objects[:]
		self._radius = 0
		self._maxDistance = 0
		self.maxObjectSize = 0
		
	def updateRadiusAndCenter(self):
		"""
		Updates the radius and center of the group. Also updates the maxObjectSize attribute.
		This method is O(n^2).
		"""
		
		self._radius = 0
		self._maxDistance = 0
		
		self.maxObjectSize = 0
		for obj in self._objects:
			if obj.size > self.maxObjectSize:
				self.maxObjectSize = obj.size	
		
		if len(self._objects) == 0:
			return
		elif len(self._objects) == 1:
			self._radius = self._objects[0].radius
			self._centralPos = self._objects[0].centralPosition.copy()
			self.arcBall.centralPos = self._centralPos
			self.arcBall.radius = self._radius
			return
		
		for a in self._objects:
			for b in self._objects:
				dist = lengthVector(a.centralPosition - b.centralPosition)
				if dist > self._maxDistance:
					pts = [a, b]
					self._maxDistance = dist
		
		# A new central position of the group is set.
		self._centralPos = (pts[0].centralPosition + pts[1].centralPosition) * 0.5
		self._radius = self._maxDistance * 0.5 + max(pts[0].radius, pts[1].radius)
		
		# Iterates over objects in the group to verify if there are any objects outside the current sphere.
		for obj in self._objects:
			dist = lengthVector(obj.centralPosition - self._centralPos) + obj.radius
			if dist > self._radius:
				self._radius = dist
		
		self.arcBall.centralPos = self._centralPos
		self.arcBall.radius = self._radius
		
	def render(self, pickingMode=False):
		"""
		Renders the group effects. Does not render the objects.
		"""
		
		if len(self._objects) == 0:
			return
		
		glPushMatrix()
		if pickingMode:
			glTranslate(*self._centralPos[:3])
			glutSolidSphere(self._radius, 20, 20)
		else:
			if self.rotatingScene:
				alpha = 0.6
			else:
				alpha = 0.2
			
			glDisable(GL_LIGHTING)
			glTranslate(*self._centralPos[:3])
			glMultMatrixf(self.rotation)
			glColor4f(0.1, 0.3, 0.5, alpha)
			glutWireSphere(self._radius + 0.005, 20, 20)
			glEnable(GL_LIGHTING)
		glPopMatrix()
		