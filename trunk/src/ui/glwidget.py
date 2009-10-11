from PyQt4.QtOpenGL import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy

from core.objects import *
from core.arcball import *
from core.util import *
from core.plane import *
from core.camera import *
from core.lighting import *

class GlWidget(QGLWidget):
	"""
	Our implementation of QGLWidget widget. :)
	 - Joaquim, el gato. Meow...
	"""
	
	def __init__ (self, parent=None):
		"""
		Widget constructor.
		"""
		
		super(GlWidget, self).__init__(parent)
				
		# Initialize window-related attributes.
		self.wWidth, self.wHeight = 0, 0
		
		# Initialize the camera.
		self.camera = Camera()
		
		# Initialize the lighting system.
		self.lighting = Lighting()
		
		# Initialize widget attributes.
		self.sceneObjects = []
		self.selectedObjects = []
		self.rotating = False
		self.mousePos = numpy.zeros(3)
		
		# Scene's arcball.
		self.sceneArcBall = SceneArcBall(self)
		
		# Initial and final screen positions of the translation.
		self.initPosition = numpy.zeros(2)
		self.finalPosition = numpy.zeros(2)
		
		# Indicates whether Ctrl is pressed or not.
		self.ctrl = False
		
		# Indicates whether the tranlation mode is activated or not.
		self.translating = False
		
		# Indicates whether there was a translation or not.
		self.objTranslated = False
		
		self.isClicked = False
		self.z = 0.0
		self.z2 = 0.0
		self.applyZoom = 0
		
	def initializeGL(self):
		"""
		Method called right before the first call to paintGL() or resizeGL().
		"""
		
		glEnable(GL_DEPTH_TEST)
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		
		# Lighting
		self.lighting.enableLighting()
		self.lighting.addLight(GL_LIGHT0)
		
		glEnable(GL_COLOR_MATERIAL)
		glClearColor(0.6, 0.7, 0.9, 1)
		
	def paintGL(self):
		"""
		Widget drawing callback.
		"""
		
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		self.render()

	def resizeGL (self, width, height):
		"""
		Resize callback.
		"""
		
		self.wWidth, self.wHeight = width, height
		glViewport(0, 0, width, height)
		self.updateGL()

	def mouseMoveEvent(self, ev):
		"""
		Mouse movement callback.
		"""
		
		# Translation
		self.translationMoveEvent()
		
		# Zoom
		self.zoomMoveEvent()
		
		# Rotation
		self.rotationMoveEvent()
		
	def mousePressEvent(self, ev):
		"""
		Mouse press callback.
		"""
		
		self.updateMousePosition()
		btn = ev.button()
		if (btn == Qt.LeftButton):
			self.leftButtonEvent()
		elif (btn == Qt.RightButton):
			self.rightButtonEvent()
		elif (btn == Qt.MidButton):
			self.midButtonEvent()
			
		print "Click (%i, %i)" % (self.mousePos[X], self.mousePos[Y])
		
	def mouseReleaseEvent(self, ev):
		"""
		Mouse release callback.
		"""
		
		self.updateMousePosition()
		
		# Rotation
		self.rotationReleaseEvent()
			
		# Zoom
		self.zoomReleaseEvent()
		
		# Translation
		self.translationReleaseEvent()

	def enterEvent(self, ev):
		"""
		Event called when the mouse enters the widget area.
		"""
		
		self.setFocus()
		self.grabKeyboard()
		
	def leaveEvent(self, ev):
		"""
		Event called when the mouse leaves the widget area.
		"""
		
		self.parent().setFocus()
		self.releaseKeyboard()
		
	def translationMoveEvent(self):
		"""
		Translation event called inside mouseMoveEvent().
		"""
		
		if self.translating:
			self.updateMousePosition()
			self.handleTranslation()
			self.updateGL()
		else:
			pass
		
	def translationReleaseEvent(self):
		"""
		Translation event called inside mouseReleaseEvent().
		"""
		
		if not(self.objTranslated) and self.translating:
			# If the objects or the scene were not translated, apply picking method
			self.handlePicking(self.mousePos[X], self.mousePos[Y])
		else:
			self.objTranslated = False
			
		self.translating = False
		
	def zoomMoveEvent(self):
		"""
		Zoom event called inside mouseMoveEvent().
		"""
		
		self.z = self.mousePos[Y]
		if self.applyZoom:
			if self.z > self.z2:
				if self.camera.fovAngle > 1:
					self.camera.fovAngle -= 1
				self.z2 = self.mousePos[Y]
				self.updateMousePosition()
				self.updateGL()
			else:
				if self.camera.fovAngle < 179:
					self.camera.fovAngle += 1
				self.z2 = self.mousePos[Y]
				self.updateMousePosition()
				self.updateGL()
		else:
			pass
		
	def zoomReleaseEvent(self):
		"""
		Zoom event called inside mouseReleaseEvent().
		"""
		
		self.applyZoom = False
		
	def rotationMoveEvent(self):
		"""
		Rotation event called inside mouseMoveEvent().
		"""
		
		if self.isClicked:
			self.updateMousePosition()
			
			if len(self.selectedObjects) == 0:
				r = self.sceneArcBall.setFinalPt(self.mousePos[X], self.mousePos[Y], True)
				self.camera.rotate(r)
				
			else:
				for obj in self.selectedObjects:
					obj.rightClickMoveEvent(self.mousePos[X], self.mousePos[Y])
			
			self.updateGL()
		
		else:
			pass
		
	def rotationReleaseEvent(self):
		"""
		Rotation event called inside mouseReleaseEvent().
		"""
		
		if self.isClicked:
			if len(self.selectedObjects) > 0:
				for obj in self.selectedObjects:
					obj.rightClickReleaseEvent(self.mousePos[X], self.mousePos[Y])
			else:
				self.rotating = False
			self.isClicked = False
			self.updateGL()
		else:
			pass
		
	def leftButtonEvent(self):
		"""
		Event called when mouse's left button is pressed.
		"""
		
		self.initPosition[X] = self.mousePos[X]
		self.initPosition[Y] = self.mousePos[Y]
		self.translating = True
		
	def rightButtonEvent(self):
		"""
		Event called when mouse's right button is pressed.
		"""
		
		self.isClicked = True
		if len(self.selectedObjects) == 0:
			self.sceneArcBall.setInitialPt(self.mousePos[X], self.mousePos[Y])
			self.rotating = True
		else:
			for obj in self.selectedObjects:
				obj.rightClickEvent(self.mousePos[X], self.mousePos[Y])
				
	def midButtonEvent(self):
		"""
		Event called when mouse's middle button is pressed.
		"""
		
		self.applyZoom = True
		self.z = self.mousePos[Y]

	def keyPressEvent(self, ev):
		"""
		Key press callback.
		"""
		
		self.updateMousePosition()
		key = str(ev.text()).upper()
		
		if (ev.modifiers() & Qt.ControlModifier):
			self.ctrl = True
			
		if (key == "C"):
			self.createCube()
			
		elif (key == "E"):
			self.createSphere()
			
		elif (key == "X"):
			self.deleteSelectedObjects()
			
		elif (key == "W"):
			self.camera.moveUp()
			self.updateGL()
			
		elif (key == "S"):
			self.camera.moveDown()
			self.updateGL()
			
		elif (key == "A"):
			self.camera.moveLeft()
			self.updateGL()
			
		elif (key == "D"):
			self.camera.moveRight()
			self.updateGL()
			
		elif (key == "F"):
			self.camera.moveForward()
			self.updateGL()
			
		elif (key == "B"):
			self.camera.moveBackward()
			self.updateGL()
			
		elif (key == "R"):
			self.camera.reset()
			self.updateGL()
		
		elif (ev.key() == Qt.Key_Up):
			self.camera.tiltUp()
			self.updateGL()
		
		elif (ev.key() == Qt.Key_Down):
			self.camera.tiltDown()
			self.updateGL()
		
		elif (ev.key() == Qt.Key_Left):
			self.camera.tiltLeft()
			self.updateGL()
		
		elif (ev.key() == Qt.Key_Right):
			self.camera.tiltRight()
			self.updateGL()
			
		elif (ev.key() == Qt.Key_Home):
			self.homeKeyPressEvent()
			
		else:
			pass
		
	def keyReleaseEvent(self, ev):
		"""
		Key release callback.
		"""
		
		if (ev.key() == Qt.Key_Control):
			self.ctrl = False
			
	def createCube(self):
		"""
		Creates a new cube.
		"""
		
		newCube = Cube(0.5, self, False)
		newCube.centralPosition = self.camera.getScenePosition(self.mousePos[X], self.mousePos[Y])
		newCube.rotation = self.camera.rotation
		self.sceneObjects.append(newCube)
		self.updateGL()
		
	def createSphere(self):
		"""
		Creates a new sphere.
		"""
		
		newSphere = Sphere(0.5, self, False)
		newSphere.centralPosition = self.camera.getScenePosition(self.mousePos[X], self.mousePos[Y])
		newSphere.rotation = self.camera.rotation
		self.sceneObjects.append(newSphere)
		self.updateGL()
		
	def deleteSelectedObjects(self):
		"""
		Deletes all selected objects.
		"""
		
		for obj in self.selectedObjects:
			self.sceneObjects.remove(obj)
		del self.selectedObjects[:]
		self.updateGL()
	
	def homeKeyPressEvent(self):
		"""
		Event called when HOME key is pressed.
		"""
		
		if len(self.sceneObjects) > 0:
			obj = self.sceneObjects[0]
			maxX = obj.centralPosition[X]
			minX = obj.centralPosition[X]
			maxY = obj.centralPosition[Y]
			minY = obj.centralPosition[Y]
			maxZ = obj.centralPosition[Z]
			minZ = obj.centralPosition[Z]
			
			for obj in self.sceneObjects:
				if obj.centralPosition[X] > maxX:
					maxX = obj.centralPosition[X]
				if obj.centralPosition[X] < minX:
					minX = obj.centralPosition[X] 
				if obj.centralPosition[Y] > maxY:
					maxY = obj.centralPosition[Y]
				if obj.centralPosition[Y] < minY:
					minY = obj.centralPosition[Y]
				if obj.centralPosition[Z] > maxZ:
					maxZ = obj.centralPosition[Z]
				if obj.centralPosition[Z] < minZ:
					minZ = obj.centralPosition[Z]
				
			sideX = abs(maxX-minX)
			sideY = abs(maxY-minY)
			sideZ = abs(maxZ-minZ)
			
			side = max(sideX, sideY)
			side = max(side, sideZ)
			
			if len(self.sceneObjects) == 1:
				side = 1
			
			positionX = (minX+maxX)/2.0
			positionY = (minY+maxY)/2.0
			positionZ = (minZ+maxZ)/2.0
			
			self.camera.position[X] = positionX - self.camera.pointer[X]*(side*sqrt(3))
			self.camera.position[Y] = positionY - self.camera.pointer[Y]*(side*sqrt(3))
			self.camera.position[Z] = positionZ - self.camera.pointer[Z]*(side*sqrt(3))
				
		else:
			self.camera.position[X] = 0 - self.camera.pointer[X]*3
			self.camera.position[Y] = 0 - self.camera.pointer[Y]*3
			self.camera.position[Z] = 0 - self.camera.pointer[Z]*3
			
		self.camera.resetFovy()
			
		self.updateGL()
		
	def updateMousePosition(self):
		"""
		Updates mousePos[X] and mousePos[Y] attributes, using GL coordinates.
		"""
		
		screenY = self.mapFromGlobal(QCursor.pos()).y()
		self.mousePos[X] = self.mapFromGlobal(QCursor.pos()).x()
		self.mousePos[Y] = glGetIntegerv(GL_VIEWPORT)[3] - screenY - 1
		
	def renderLighting(self):
		"""
		Sets the lighting of the scene.
		"""
		
		self.lighting.setLight(GL_LIGHT0, [1.0, 1.0, 1.0, 0],
							[1.0, 1.0, 1.0, 1.0],
							[0, 0, 0, 1.0],
							[0.2, 0.2, 0.2, 1.0])
		
	def renderAxis(self):
		"""
		Creates a small white wire sphere and the XYZ axis in the 0 coordinate, just for reference.
		"""
		
		# White wire
		glColor(1, 1, 1)
		glutWireSphere(0.1, 20, 20)
		
		# XYZ axis
		glLineWidth(2)
		glDisable(GL_LIGHTING)
		glBegin(GL_LINES)
		glColor(1, 0, 0)
		glVertex(0, 0, 0)
		glVertex(1, 0, 0)
		glColor(0, 1, 0)
		glVertex(0, 0, 0)
		glVertex(0, 1, 0)
		glColor(0, 0, 1)
		glVertex(0, 0, 0)
		glVertex(0, 0, 1)
		glEnd()
		glEnable(GL_LIGHTING)
		glLineWidth(1)
		
	def renderArcBall(self):
		"""
		Creates a small wire sphere centered on the scene's rotation center
		that approximatly bounds the visualization volume.
		"""
		
		if self.rotating:
			alpha = 0.6
		else:
			alpha = 0.2
			
		rotCenter = (self.camera.position + self.camera.pointer*10)[:3]
		glColor4f(0.1, 0.3, 0.5, alpha)
		glTranslate(*rotCenter)
		glDisable(GL_LIGHTING)
		glutWireSphere(10, 20, 20)
		glEnable(GL_LIGHTING)
		glTranslate(*-rotCenter)	
		
	def render(self):
		"""
		Renders the scene.
		Warning: This method sets the matrix mode to GL_MODELVIEW.
		"""
		
		# Camera
		self.camera.setLens(self.wWidth, self.wHeight)
		self.camera.setView()
		
		# Lighting
		self.renderLighting()
		
		# Reference of the XYZ axis
		self.renderAxis()
		
		for obj in self.sceneObjects:
			glPushMatrix()
			obj.render()
			glPopMatrix()
			
		# Reference to ArcBall
		self.renderArcBall()
		
	def handleTranslation(self):
		"""
		Handles object translation when the user drags the object with the mouse's left button.
		"""
		
		self.finalPosition[X] = self.mousePos[X]
		self.finalPosition[Y] = self.mousePos[Y]
		shift = (self.finalPosition - self.initPosition) / self.wHeight
		
		if (shift[X] != 0) or (shift[Y] != 0):
			self.objTranslated = True
			
		if len(self.selectedObjects) == 0:
			self.camera.position -= shift[Y]*self.camera.upVector*2
			self.camera.position += shift[X]*self.camera.leftVector*2
		else:
			for obj in self.selectedObjects:
				screenPos = gluProject(*obj.centralPosition[:3])
				newPos = gluUnProject(self.mousePos[X], self.mousePos[Y], screenPos[Z])
				for i in range(3):
					obj.centralPosition[i] = newPos[i]
			
		self.initPosition[X] = self.finalPosition[X]
		self.initPosition[Y] = self.finalPosition[Y]
			
	def handlePicking(self, x, y):
		"""
		Handles object picking when the user clicks with the mouse's left button.
		"""
		
		buffer = glSelectBuffer(len(self.sceneObjects)*4)
		projection = glGetDoublev(GL_PROJECTION_MATRIX)
		viewport = glGetIntegerv(GL_VIEWPORT)
		
		glRenderMode(GL_SELECT)
		
		glMatrixMode(GL_PROJECTION)
		glPushMatrix()
		glLoadIdentity()
		gluPickMatrix(x, y, 2, 2, viewport)
		glMultMatrixf(projection)
		
		self.camera.setView()
		
		glInitNames()
		glPushName(0)
		
		for i in range(len(self.sceneObjects)):
			glPushMatrix()
			glLoadName(i)
			self.sceneObjects[i].render()
			glPopMatrix()
				
		glMatrixMode(GL_PROJECTION)
		glPopMatrix()
		glMatrixMode(GL_MODELVIEW)
		glFlush()
		
		glPopName()
			
		hits = glRenderMode(GL_RENDER)
		
		nearestHit = None
		for hit in hits:
			near, far, names = hit
			if (nearestHit == None) or (near < nearestHit[0]):
				nearestHit = [near, names[0]]
		
		if nearestHit != None:
			# An object was picked.
			pickedObject = self.sceneObjects[nearestHit[1]]
			
			if not(self.ctrl):
				# CTRL is not pressed.
				if len(self.selectedObjects) == 1 \
				and self.selectedObjects[0] == pickedObject:
					# The only object that was previously selected is the one picked.
					pickedObject.select(False)
					del self.selectedObjects[:]
				else:
					# Deselect all previously selected objects.
					for obj in self.selectedObjects:
						obj.select(False)
					del self.selectedObjects[:]
					
					# Select the picked object.
					pickedObject.select(True)
					self.selectedObjects.append(pickedObject)
			else:
				# CTRL is pressed.
				if pickedObject.selected:
					pickedObject.select(False)
					self.selectedObjects.remove(pickedObject)
				else:
					pickedObject.select(True)
					self.selectedObjects.append(pickedObject)
		elif not(self.ctrl):
			# No objects were picked and CTRL is not pressed.
			for obj in self.selectedObjects:
				obj.select(False)
			del self.selectedObjects[:]
			
		self.updateGL()
