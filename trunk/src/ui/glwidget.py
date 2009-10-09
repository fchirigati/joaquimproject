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

class GlWidget(QGLWidget):
	"""
	Our implementation of QGLWidget widget. :) - Joaquim, el gato. Meow...
	"""
	
	def __init__ (self, parent=None):
		"""
		Widget constructor.
		"""
		
		super(GlWidget, self).__init__(parent)
		
		# Enables mouse move events even if no button is pressed.
		self.setMouseTracking(True)
		
		# Initialize window-related attributes.
		self.wWidth, self.wHeight = 0, 0
		
		# Initialize widget attributes.
		self.sceneObjects = []
		self.selectedObjects = []
		self.rotation = numpy.identity(4)
		self.rotating = False
		self.mousePos = numpy.zeros(3)
		
		# Camera's absolute position in world coordinates.
		self.position = numpy.array([0.0, 0.0, 3.0, 1])
		# Camera's up vector. Should always be unitary.
		self.upVector = numpy.array([0.0, 1.0, 0.0, 0])
		# Vector that points to the direction that the camera is looking. Always unitary.
		self.pointer = numpy.array([0.0, 0.0, -1.0, 0])
		# Camera's scale factor.
		self.scale = numpy.array([1.0, 1.0, 1.0])
		# Near/far clipping plane values.
		self.near, self.far = 1, 500
		# Perspective angle (in degrees).
		self.fovAngle = 45
		
		# Scene's arcball.
		self.boundingSphere = SceneArcBall(self)
		
		# Initial and final positions of the translation.
		self.initPosition = numpy.zeros(4)
		self.finalPosition = numpy.zeros(4)
		
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
		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)
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
				self.position[Z] -= 0.2
				self.z2 = self.mousePos[Y]
				self.updateMousePosition()
				self.updateGL()
			else:
				self.position[Z] += 0.2
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
				r = self.boundingSphere.setFinalPt(self.mousePos[X], self.mousePos[Y], True)
				rotCenter = (self.position + self.pointer*10)[:3]
				
				glMatrixMode(GL_MODELVIEW)
				glPushMatrix()
				glLoadIdentity()
				glTranslate(*rotCenter)
				glMultMatrixd(r)
				glTranslate(*(-rotCenter))
				self.position = multiplyByMatrix(self.position)
				self.upVector = multiplyByMatrix(self.upVector)
				self.pointer = multiplyByMatrix(self.pointer)
				glPopMatrix()
				
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
		
		self.initPosition = numpy.array([self.mousePos[X], self.mousePos[Y],
										 self.mousePos[Z], 1])
		self.translating = True
		
	def rightButtonEvent(self):
		"""
		Event called when mouse's right button is pressed.
		"""
		
		self.isClicked = True
		if len(self.selectedObjects) == 0:
			self.boundingSphere.setInitialPt(self.mousePos[X], self.mousePos[Y])
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
			self.drawCube()
			
		elif (key == "E"):
			self.drawSphere()
			
		elif (key == "X"):
			self.deleteObjects()
			
		elif (key == "W"):
			self.position[Y] += 0.2
			self.updateGL()
			
		elif (key == "S"):
			self.position[Y] -= 0.2
			self.updateGL()
			
		elif (key == "A"):
			self.position[X] -= 0.3
			self.updateGL()
			
		elif (key == "D"):
			self.position[X] += 0.3
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
			
	def drawCube(self):
		"""
		Draws a new cube.
		"""
		
		newCube = Cube(0.5, self, False)
		print self.getMouseScenePosition()
		newCube.setCentralPosition(self.getMouseScenePosition())
		newCube.setRotationMatrix(self.rotation)
		self.sceneObjects.append(newCube)
		self.updateGL()
		
	def drawSphere(self):
		"""
		Draws a new sphere.
		"""
		
		newSphere = Sphere(0.5, self, False)
		newSphere.setCentralPosition(self.getMouseScenePosition())
		newSphere.setRotationMatrix(self.rotation)
		self.sceneObjects.append(newSphere)
		self.updateGL()
		
	def deleteObjects(self):
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
			for obj in self.sceneObjects:
				maxX = obj.centralPos[X]
				minX = obj.centralPos[X]
				maxY = obj.centralPos[Y]
				minY = obj.centralPos[Y]
				maxZ = obj.centralPos[Z]
				maxN = obj.centralPos[Z]
				break
			
			for obj in self.sceneObjects:
				if obj.centralPos[X] > maxX:
					maxX = obj.centralPos[X]
				if obj.centralPos[X] < minX:
					minX = obj.centralPos[X] 
				if obj.centralPos[Y] > maxY:
					maxY = obj.centralPos[Y]
				if obj.centralPos[Y] < minY:
					minY = obj.centralPos[Y]
				if obj.centralPos[Z] > maxZ:
					maxZ = obj.centralPos[Z]
				
			maxN = max(abs(maxX-minX),abs(maxY-minY))
			self.position[X] = (minX+maxX)/2.0
			self.position[Y] = (minY+maxY)/2.0
			self.position[Z] = maxN/tan(22.5*pi/180) + abs(maxZ) + 2
				
		else:
			self.position[X] = 0
			self.position[Y] = 0
			self.position[Z] = 3
			
		self.updateGL()
		
	def updateMousePosition(self):
		"""
		Updates mousePos[X] and mousePos[Y] attributes, using GL coordinates.
		"""
		
		screenY = self.mapFromGlobal(QCursor.pos()).y()
		self.mousePos[X] = self.mapFromGlobal(QCursor.pos()).x()
		self.mousePos[Y] = glGetIntegerv(GL_VIEWPORT)[3] - screenY - 1
		#self.mousePos[Z] = glReadPixels(self.mousePos[X], self.mousePos[Y],
		#								1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)
			
	def getMouseScenePosition(self):
		"""
		Gets the coordinates of the mouse in the scene.
		"""
		
		self.updateMousePosition()

		# Objects are created in mousePos[Z] = 0.5.
		self.mousePos[Z] = 0.5
		
		coordPosition = gluUnProject(*self.mousePos)
		
		return arrayToVector(coordPosition, 1)
	
	def __setCameraView(self):
		"""
		Sets the camera to the current lookAt position and rotation angle.
		Warning: This method sets the matrix mode to GL_MODELVIEW.
		"""
		
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		
		gluLookAt(self.position[X], self.position[Y], self.position[Z], \
				self.position[X] + self.pointer[X], self.position[Y] + self.pointer[Y], self.position[Z] + self.pointer[Z], \
				self.upVector[X], self.upVector[Y], self.upVector[Z])
		glScale(self.scale[X], self.scale[Y], self.scale[Z])
		
	def render(self):
		"""
		Renders the scene.
		Warning: This method sets the matrix mode to GL_MODELVIEW.
		"""
		
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(self.fovAngle, float(self.wWidth)/self.wHeight, self.near, self.far)
		
		self.__setCameraView()
		
		light0_pos = [1.0, 1.0, 1.0, 0]
		diffuse0 = [1.0, 1.0, 1.0, 1.0]
		specular0 = [0, 0, 0, 1.0]
		ambient0 = [0.2, 0.2, 0.2, 1.0]

		glLightfv(GL_LIGHT0, GL_POSITION, light0_pos)
		glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse0)
		glLightfv(GL_LIGHT0, GL_SPECULAR, specular0)
		glLightfv(GL_LIGHT0, GL_AMBIENT, ambient0)
		
		# Creates a small white wire sphere and the XYZ axis in the 0 coordinate, just for refernece.
		glColor(1, 1, 1)
		glutWireSphere(0.1, 20, 20)
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
		
		for obj in self.sceneObjects:
			glPushMatrix()
			obj.render()
			glPopMatrix()
			
		# Create a small wire sphere centered on the scene's rotation center
		# that approximatly bounds the visualization volume.
		if self.rotating:
			alpha = 0.6
		else:
			alpha = 0.2
			
		rotCenter = (self.position + self.pointer*10)[:3]
		glColor4f(0.1, 0.3, 0.5, alpha)
		glTranslate(*rotCenter)
		glDisable(GL_LIGHTING)
		glutWireSphere(10, 20, 20)
		glEnable(GL_LIGHTING)
		glTranslate(*-rotCenter)
		
		#if not self.rotating:
		#glDepthMask(GL_TRUE)
		
	def handleTranslation(self):
		"""
		Handles object translation when the user drags the object with the mouse's left button.
		"""
		
		self.finalPosition = numpy.array([self.mousePos[X], self.mousePos[Y],
										  self.mousePos[Z], 1])
		shift = vector(self.initPosition, self.finalPosition)
		
		if ((shift[0] != 0) or (shift[1] != 0) or (shift[2] != 0)):
			self.objTranslated = True
			
		shift = shift/100
		if len(self.selectedObjects) == 0:
			self.position = applyVector(self.position, -shift)
		else:
			for obj in self.selectedObjects:
				obj.setCentralPosition(applyVector(obj.getCentralPosition(), shift))
		self.initPosition = self.finalPosition
			
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
		
		self.__setCameraView()
		
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
				if pickedObject.isSelected():
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
