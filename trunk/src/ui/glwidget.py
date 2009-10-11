from PyQt4.QtOpenGL import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy

from core.arcball import *
from core.camera import *
from core.group import *
from core.lighting import *
from core.objects import *
from core.plane import *
from core.util import *

class GlWidget(QGLWidget):
	"""
	Implementation of the QGLWidget widget.
	Joaquim, el gato. Miau! :D
	(Quem tinha tirado meu miado? - K.)
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
		self.selectedObjects = Group(self)
		self.mousePos = numpy.zeros(3)
		
		# Scene's arcball.
		self.sceneArcBall = SceneArcBall(self)
		
		# Last mouse position, updated at the end of the mouse events.
		self.lastMousePos = numpy.zeros(2)
		
		# Object that cannot be deselected in mouse release event,
		# once it was selected in mouse press event.
		self.preSelectedObject = None
		
		# Indicates whether Ctrl is pressed or not.
		self.ctrlPressed = False
		
		# Indicates whether the mouse buttons are pressed or not.
		self.leftClicked = False
		self.middleClicked = False
		self.rightClicked = False
		
		# Indicares whether there was a translation or not.
		self.objTranslated = False
		self.rotatingScene = False
		
		self.z = 0.0
		self.z2 = 0.0
		
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
		
		self.updateMousePosition()
		
		# Translation
		self.translationMoveEvent()
		
		# Zoom
		self.zoomMoveEvent()
		
		# Rotation
		self.rotationMoveEvent()
		
		self.lastMousePos[X] = self.mousePos[X]
		self.lastMousePos[Y] = self.mousePos[Y]
		
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
			
		self.lastMousePos[X] = self.mousePos[X]
		self.lastMousePos[Y] = self.mousePos[Y]
		
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
		
		self.lastMousePos[X] = self.mousePos[X]
		self.lastMousePos[Y] = self.mousePos[Y]

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
		
		if self.leftClicked:
			self.updateMousePosition()
			self.handleTranslation()
			self.updateGL()
		
	def translationReleaseEvent(self):
		"""
		Translation event called inside mouseReleaseEvent().
		"""
		
		if self.leftClicked:
			if not self.objTranslated:
				# If there was a translation, do not apply a deselection event.
				self.releaseEventPicking()
			else:
				self.objTranslated = False
		
		self.leftClicked = False
		
	def zoomMoveEvent(self):
		"""
		Zoom event called inside mouseMoveEvent().
		"""
		
		self.z = self.mousePos[Y]
		if self.middleClicked:
			if self.z > self.z2:
				self.camera.zoomIn()
				self.z2 = self.mousePos[Y]
				self.updateMousePosition()
				self.updateGL()
			else:
				self.camera.zoomOut()
				self.z2 = self.mousePos[Y]
				self.updateMousePosition()
				self.updateGL()
		
	def zoomReleaseEvent(self):
		"""
		Zoom event called inside mouseReleaseEvent().
		"""
		
		self.middleClicked = False
		
	def rotationMoveEvent(self):
		"""
		Rotation event called inside mouseMoveEvent().
		"""
		
		if self.rightClicked:
			self.updateMousePosition()
			
			if self.rotatingScene:
				r = self.sceneArcBall.setFinalPt(self.mousePos[X], self.mousePos[Y], True)
				self.camera.rotate(r)
			else:
				self.selectedObjects.rightClickMoveEvent(self.mousePos[X], self.mousePos[Y])
			
			self.updateGL()
		
	def rotationReleaseEvent(self):
		"""
		Rotation event called inside mouseReleaseEvent().
		"""
		
		if self.rightClicked:
			if self.rotatingScene:
				self.rotatingScene = False
			else:
				self.selectedObjects.rightClickReleaseEvent(self.mousePos[X], self.mousePos[Y])
			self.rightClicked = False
			self.updateGL()
		
	def leftButtonEvent(self):
		"""
		Event called when mouse's left button is pressed.
		"""
		
		self.lastMousePos[X] = self.mousePos[X]
		self.lastMousePos[Y] = self.mousePos[Y]
		
		self.pressEventPicking()
		self.leftClicked = True
		
	def rightButtonEvent(self):
		"""
		Event called when mouse's right button is pressed.
		"""
		
		if self.mouseOverGroup():
			self.selectedObjects.rightClickEvent(self.mousePos[X], self.mousePos[Y])
		else:
			# The mouse was pressed outside the group selection sphere.
			self.sceneArcBall.setInitialPt(self.mousePos[X], self.mousePos[Y])
			self.rotatingScene = True
			
		self.rightClicked = True
				
	def midButtonEvent(self):
		"""
		Event called when mouse's middle button is pressed.
		"""
		
		self.middleClicked = True
		self.z = self.mousePos[Y]

	def keyPressEvent(self, ev):
		"""
		Key press callback.
		"""
		
		self.updateMousePosition()
		key = str(ev.text()).upper()
		
		if (ev.modifiers() & Qt.ControlModifier):
			self.ctrlPressed = True
			
		if (key == "C"):
			self.createCube()
			self.updateGL()
		elif (key == "E"):
			self.createSphere()
			self.updateGL()
		elif (key == "X"):
			self.deleteSelectedObjects()
			self.updateGL()
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
			self.updateGL()
		
	def keyReleaseEvent(self, ev):
		"""
		Key release callback.
		"""
		
		if (ev.key() == Qt.Key_Control):
			self.ctrlPressed = False
			
	def createCube(self):
		"""
		Creates a new cube.
		"""
		
		newCube = Cube(0.5, self, False)
		newCube.centralPosition = self.camera.getScenePosition(self.mousePos[X], self.mousePos[Y])
		newCube.rotation = self.camera.rotation
		self.sceneObjects.append(newCube)
		
	def createSphere(self):
		"""
		Creates a new sphere.
		"""
		
		newSphere = Sphere(0.5, self, False)
		newSphere.centralPosition = self.camera.getScenePosition(self.mousePos[X], self.mousePos[Y])
		newSphere.rotation = self.camera.rotation
		self.sceneObjects.append(newSphere)
		
	def deleteSelectedObjects(self):
		"""
		Deletes all selected objects.
		"""
		
		for obj in self.selectedObjects:
			self.sceneObjects.remove(obj)
		self.selectedObjects.removeAll()
	
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
		
		glPushMatrix()
		self.selectedObjects.render()
		glPopMatrix()
		
	def handleTranslation(self):
		"""
		Handles object translation when the user drags the object with the mouse's left button.
		"""
		
		if (self.lastMousePos[X] != self.mousePos[X]) or (self.lastMousePos[Y] != self.mousePos[Y]):
			self.objTranslated = True
			
		if len(self.selectedObjects) == 0:
			shift = self.camera.getScenePosition(*self.lastMousePos[:2]) \
					- self.camera.getScenePosition(self.mousePos[X], self.mousePos[Y])
			self.camera.position += shift
		else:
			self.selectedObjects.leftClickMoveEvent(self.mousePos[X], self.mousePos[Y])
		
	def tryPick(self):
		"""
		Handles object picking, returning the object under the current mouse position.
		Returns None if there is none.
		"""
		
		buffer = glSelectBuffer(len(self.sceneObjects)*4)
		projection = glGetDouble(GL_PROJECTION_MATRIX)
		viewport = glGetInteger(GL_VIEWPORT)
		
		glRenderMode(GL_SELECT)
		
		glMatrixMode(GL_PROJECTION)
		glPushMatrix()
		glLoadIdentity()
		gluPickMatrix(self.mousePos[X], self.mousePos[Y], 2, 2, viewport)
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
			return self.sceneObjects[nearestHit[1]]
				
		return nearestHit
	
	def mouseOverGroup(self):
		"""
		Tries to pick the selected group sphere.
		Returns True if succeeded and False otherwise.
		"""
		
		if len(self.selectedObjects) == 0:
			return False
		
		buffer = glSelectBuffer(4)
		projection = glGetDouble(GL_PROJECTION_MATRIX)
		viewport = glGetInteger(GL_VIEWPORT)
		
		glRenderMode(GL_SELECT)
		
		glMatrixMode(GL_PROJECTION)
		glPushMatrix()
		glLoadIdentity()
		gluPickMatrix(self.mousePos[X], self.mousePos[Y], 2, 2, viewport)
		glMultMatrixf(projection)
		self.camera.setView()
		
		glInitNames()
		glPushName(0)
		
		glPushMatrix()
		glLoadName(0)
		self.selectedObjects.render(True)
		glPopMatrix()
				
		glMatrixMode(GL_PROJECTION)
		glPopMatrix()
		glMatrixMode(GL_MODELVIEW)
		glFlush()
		glPopName()
			
		hits = glRenderMode(GL_RENDER)
				
		return len(hits) > 0
			
	def pressEventPicking(self):
		"""
		Picking event called when mousePressEvent() is called.
		Note that this event will be called before translationMoveEvent(),
		and so, it does not consider the translation event.
		"""
		
		pickedObject = self.tryPick()
		
		if pickedObject != None:
			# An object was picked.
			
			if not(self.ctrlPressed):
				# CTRL is not pressed.
				
				if pickedObject in self.selectedObjects:
					# The picked object is already selected.
					# releaseEventPicking
					pass
				
				else:
					# The picked object was not previously selected.
					
					# Deselect all previously selected objects.
					self.selectedObjects.removeAll()
					
					# Select the picked object.
					self.selectedObjects.add(pickedObject)
				
					self.preSelectedObject = pickedObject
			else:
				# CTRL is pressed.
				
				if pickedObject.selected:
					pass
				else:
					self.selectedObjects.add(pickedObject)
					self.preSelectedObject = pickedObject
			
			self.selectedObjects.leftClickPressEvent(self.mousePos[X], self.mousePos[Y])		
		else:
			# No objects were picked.
			self.selectedObjects.removeAll()
			
		self.updateGL()
		
	def releaseEventPicking(self):
		"""
		Picking event called when mouseReleaseEvent() is called.
		Note that this event will be called in translationReleaseEvent(),
		and so, it will not be called if there was a previous translation
		in translationMoveEvent().
		"""
		
		pickedObject = self.tryPick()
		
		if self.preSelectedObject != pickedObject and pickedObject != None:
			# The picked object was not the one clicked in pressEventPicking() and an object was picked.
				
			if not(self.ctrlPressed):
			# CTRL is not pressed.
			
				if pickedObject in self.selectedObjects:
					# The picked object is already selected.
					
					if len(self.selectedObjects) > 1:
						# There were more than one object previously selected.
						
						# Deselect all previously selected objects.
						self.selectedObjects.removeAll()
						
						# Select the picked object.
						self.selectedObjects.add(pickedObject)
						
					else:
						# The picked object is the previously selected object.
						self.selectedObjects.remove(pickedObject)
					
			else:
			# CTRL is pressed.
				if pickedObject.selected:
					self.selectedObjects.remove(pickedObject)
				
		elif self.preSelectedObject == pickedObject:
			self.preSelectedObject = None
			
		self.updateGL()
		