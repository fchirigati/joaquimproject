from PyQt4.QtOpenGL import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy

from about_dialog import *
from help_dialog import *

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
	"""
	
	def __init__ (self, mainWindow, parent):
		"""
		Widget constructor.
		"""
		
		super(GlWidget, self).__init__(parent)
				
		# MainWindow reference.
		self.mainWindow = mainWindow
				
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
		
		# Indicates whether if the user is editing or not a slider.
		self.editingSizeSlider = False
		self.editingZoomSlider = False
		
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
		self.lighting.setLight(GL_LIGHT0, [1.0, 1.0, 1.0, 0],
										[1.0, 1.0, 1.0, 1.0],
										[0, 0, 0, 1.0],
										[0.2, 0.2, 0.2, 1.0])
		
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
		
	def mousePressEvent(self, ev):
		"""
		Mouse press callback.
		"""
		
		self.updateMousePosition()
		btn = ev.button()
		
		if (btn == Qt.LeftButton):
			self.pressEventPicking()
			self.leftClicked = True
			
		elif (btn == Qt.RightButton):
			if self.mouseOverGroup():
				self.selectedObjects.rightClickEvent(self.mousePos[X], self.mousePos[Y])
			else:
				self.sceneArcBall.setInitialPt(self.mousePos[X], self.mousePos[Y])
				self.rotatingScene = True	
			self.rightClicked = True
			
		elif (btn == Qt.MidButton):
			self.middleClicked = True
		
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
				
	def selectAll(self):
		"""
		Selects all objects.
		"""
		
		for obj in self.sceneObjects:
			if obj not in self.selectedObjects:
				self.selectedObjects.add(obj)
		
		self.updateGL()
		
	def translationMoveEvent(self):
		"""
		Translation event called inside mouseMoveEvent().
		"""
		
		if self.leftClicked:
			self.handleTranslation()
			self.updateGL()
		
	def translationReleaseEvent(self):
		"""
		Translation event called inside mouseReleaseEvent().
		"""
		
		if self.leftClicked:
			if not(self.objTranslated):
				# If there was a translation, do not apply a deselection event.
				self.releaseEventPicking()
			else:
				self.objTranslated = False
		
		self.leftClicked = False
		
	def zoomMoveEvent(self):
		"""
		Zoom event called inside mouseMoveEvent().
		"""
		
		if self.middleClicked:
			if self.lastMousePos[Y] < self.mousePos[Y]:
				self.camera.zoomIn()
				self.updateGL()
			elif self.lastMousePos[Y] > self.mousePos[Y]:
				self.camera.zoomOut()
				self.updateGL()
			self.mainWindow.zoomSlider.setValue(int(self.camera.fovAngle))
		
		self.updateGL()
		
	def zoomOut(self):
		"""
		Zooms the camera out.
		"""
		
		self.camera.zoomOut()
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
			self.resetView()
		elif (key == "T"):
			self.selectAll()
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
			self.viewAll()
		
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
		
		newCube = Cube(self, self.mainWindow.sizeSlider.value()*0.1)
		newCube.centralPosition = self.camera.getScenePosition(self.mousePos[X], self.mousePos[Y])
		newCube.rotation = self.camera.rotation
		self.sceneObjects.append(newCube)
		
	def createSphere(self):
		"""
		Creates a new sphere.
		"""
		
		newSphere = Sphere(self, self.mainWindow.sizeSlider.value()*0.1)
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
		
	def resetView(self):
		"""
		Resets the view.
		"""
		
		self.camera.reset()
		self.mainWindow.zoomSlider.setValue(int(self.camera.fovAngle))
		self.updateGL()
	
	def viewAll(self):
		"""
		Event called when HOME key is pressed.
		"""
		
		if len(self.sceneObjects) == 0:
			return
		
		group = Group(self)
		for obj in self.sceneObjects:
			group.add(obj, False)
		
		self.camera.resetFovy()
		self.mainWindow.zoomSlider.setValue(int(self.camera.fovAngle))
		dist = group.radius / sin(radians(self.camera.fovAngle * 0.5))
		self.camera.position = group.centralPosition - self.camera.pointer * dist
		
		self.updateGL()
		
	def updateMousePosition(self):
		"""
		Updates mousePos and lastMousePos attributes, using GL coordinates.
		"""
		
		screenY = self.mapFromGlobal(QCursor.pos()).y()
		
		self.lastMousePos[X] = self.mousePos[X]
		self.lastMousePos[Y] = self.mousePos[Y]
		
		self.mousePos[X] = self.mapFromGlobal(QCursor.pos()).x()
		self.mousePos[Y] = glGetIntegerv(GL_VIEWPORT)[3] - screenY - 1
		
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
		glVertex3f(0, 0, 0)
		glVertex3f(1, 0, 0)
		glColor(0, 1, 0)
		glVertex3f(0, 0, 0)
		glVertex3f(0, 1, 0)
		glColor(0, 0, 1)
		glVertex3f(0, 0, 0)
		glVertex3f(0, 0, 1)
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
		self.lighting.render()
		
		# Reference of the XYZ axis
		self.renderAxis()
		
		for obj in self.sceneObjects:
			obj.render()
		
		self.selectedObjects.render()
		
	def handleTranslation(self):
		"""
		Handles object translation when the user drags an object with the mouse's left button.
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
		
		if len(self.sceneObjects) == 0:
			return None
		
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
			glLoadName(i)
			self.sceneObjects[i].render()
				
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
		
		glLoadName(0)
		self.selectedObjects.render(True)
				
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
			
		if len(self.selectedObjects) > 0:
			self.mainWindow.sizeSlider.setValue(self.selectedObjects.maxObjectSize * 10)
			
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

		if len(self.selectedObjects) > 0:
			self.mainWindow.sizeSlider.setValue(self.selectedObjects.maxObjectSize * 10)
		self.updateGL()

	def showAboutEvent(self):
		"""
		Shows the about dialog.
		"""
		
		aboutMessage = AboutDialog()
		aboutMessage.exec_()
		
	def showHelpEvent(self):
		"""
		Shows the help dialog.
		"""
		
		aboutMessage = HelpDialog()
		aboutMessage.exec_()
		
	def quitEvent(self):
		"""
		Method called when the menu Quit button is pressed.
		"""
		
		pass
	
	def zoomSliderChangeEvent(self):
		"""
		Method called when the user changes the zoom slider value.
		"""
		
		if self.editingZoomSlider:
			self.camera.fovAngle = self.mainWindow.zoomSlider.value()
			self.updateGL()
		
	def zoomSliderPressedEvent(self):
		"""
		Method called when the zoom slider is pressed.
		"""
		
		self.editingZoomSlider = True
		
	def zoomSliderReleasedEvent(self):
		"""
		Method called when the zoom slider is released.
		"""
		
		self.editingZoomSlider = False
	
	def sizeSliderChangeEvent(self):
		"""
		Changes the size of the selected objects to value.
		"""
		
		if self.editingSizeSlider:
			size = self.mainWindow.sizeSlider.value() * 0.1
			for obj in self.selectedObjects:
				obj.size = size
			self.selectedObjects.updateRadiusAndCenter()
				
			self.updateGL()

	def sizeSliderPressedEvent(self):
		"""
		Method called when the size slider is pressed.
		"""
		
		self.editingSizeSlider = True
		
	def sizeSliderReleasedEvent(self):
		"""
		Method called when the size slider is released.
		"""
		
		self.editingSizeSlider = False
		
	