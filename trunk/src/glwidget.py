from PyQt4.QtOpenGL import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy

from objects import *
from arcball import *
from util import *

class GlWidget(QGLWidget):
	"""Our implementation of QGLWidget widget. :) - Joaquim, el gato."""
	
	def __init__ (self, parent=None):
		"""Widget constructor."""
		
		super(GlWidget, self).__init__(parent)
		
		# Enables mouse move events even if a button is not pressed.
		self.setMouseTracking(True)
		
		# Initialize widget attributes.
		self.sceneObjects = []
		self.rotation = numpy.identity(4) 
		self.boundingSphere = ArcBall()
		self.boundingSphere.setCentralPosition([0, 0, 0])
		self.boundingSphere.setRadius(1)
		
		self.selectedObject = None
		self.isClicked = False
		self.mousePosX = 0.0
		self.mousePosY = 0.0
		self.mousePosZ = 0.0
		self.move = 0.0
		self.z = 0.0
		self.z2 = 0.0
		self.zoom = 0.5
		self.applyZoom = 0
		
	def initializeGL(self):
		
		glEnable(GL_DEPTH_TEST)
		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)
		glEnable(GL_COLOR_MATERIAL)
		
	def paintGL(self):
		"""Widget drawing callback."""
		
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		self.render()

	def resizeGL (self, width, height):
		"""Resize callback."""
		
		side = min(width,height)
		glViewport((width - side) / 2, (height - side) / 2, side, side)
		self.updateGL()

	def mouseMoveEvent(self, ev):
		""""Mouse movement callback."""
		self.z = self.mousePosY
		if self.applyZoom:
			if self.z > self.z2:
				#self.zoom -= abs(self.zoom - self.z)/750
				self.zoom += 0.2
				self.z2 = self.mousePosY
				self.updateMousePosition()
				self.updateGL()
			else:
				#self.zoom += abs(self.zoom - self.z)/750
				self.zoom -= 0.2
				self.z2 = self.mousePosY
				self.updateMousePosition()
				self.updateGL() 
		
		if (self.isClicked):
			self.updateMousePosition()
			r = self.boundingSphere.setFinalPt(self.mousePosX, self.mousePosY)
			self.rotation = self.rotation*r
			self.update()
		
	def mousePressEvent(self, ev):
		"""Mouse press callback."""
		
		self.updateMousePosition()
		btn = ev.button()
		if (btn == Qt.LeftButton):
			btn = "Left"
			self.pickingObjects(self.mousePosX, self.mousePosY)
		elif (btn == Qt.RightButton):
			btn = "Right"
			self.isClicked = True
			self.boundingSphere.setInitialPt(self.mousePosX, self.mousePosY)
			#self.applyZoom = True
			#self.z = self.mousePosY
		elif (btn == Qt.MidButton):
			btn = "Middle"
			self.applyZoom = True
			self.z = self.mousePosY
		else:
			btn = "Joaquim"
		print "Click: %s (%i, %i)" % (btn, self.mousePosX, self.mousePosY)
#		
	def mouseReleaseEvent(self, ev):
		"""Mouse release callback."""
		
		self.isClicked = False
		self.applyZoom = False	 

	def enterEvent(self, ev):
		"""Event called when the mouse enters the widget area."""
		
		self.setFocus()
		self.grabKeyboard()
		
	def leaveEvent(self, ev):
		"""Event called when the mouse leaves the widget area."""
		
		self.parent().setFocus()
		self.releaseKeyboard()

	def keyPressEvent(self, ev):
		"""Key press callback."""
		
		self.updateMousePosition()
		key = str(ev.text()).upper()
		if (key == "C"):
			newCube = Cube(0.5, False)
			newCube.setCentralPosition(self.getMouseScenePosition())
			newCube.setRotationMatrix(self.rotation)
			self.sceneObjects.append(newCube)
			self.updateGL()
		elif (key == "E"):
			newSphere = Sphere(0.5, False)
			newSphere.setCentralPosition(self.getMouseScenePosition())
			newSphere.setRotationMatrix(self.rotation)
			self.sceneObjects.append(newSphere)
			self.updateGL()
		elif (key == "W"):
			self.zoom += 0.2
			self.updateGL()
		elif (key == "S"):
			self.zoom -= 0.2
			self.updateGL()
		elif (key == "A"):
			self.move += 0.3
			self.updateGL()
		elif (key == "D"):
			self.move -= 0.3
			self.updateGL()
		else:
			pass
		
	def updateMousePosition(self):
		"""Updates mousePosX and mousePosY attributes, using GL coordinates."""
		
		screenY = self.mapFromGlobal(QCursor.pos()).y()
		self.mousePosX = self.mapFromGlobal(QCursor.pos()).x()
		self.mousePosY = glGetIntegerv(GL_VIEWPORT)[3] - screenY - 1
			
	def getMouseScenePosition(self):
		"""Gets the coordinates of the mouse in the scene. Since we cannot recover the Z coordinate, so we just give it a fixed value: 0.5."""
		
		self.updateMousePosition()
		#self.mousePosZ = glReadPixels(self.mousePosX, self.mousePosY, 1, 1, 
		#							  GL_DEPTH_COMPONENT, GL_FLOAT)
		self.mousePosZ = 0.5
		
		self.coordPosition = gluUnProject(self.mousePosX, self.mousePosY, self.mousePosZ,
										  glGetDoublev(GL_MODELVIEW_MATRIX),
										  glGetDoublev(GL_PROJECTION_MATRIX),
										  glGetIntegerv(GL_VIEWPORT))
		
		return self.coordPosition
		
	def render(self):
				
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(45, 1, 1, 500)
		
		glTranslate(self.move,0,self.zoom)
		
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		glTranslate(0, 0, -3)
		glMultMatrixf(self.rotation)
		#gluLookAt(self.move, 0.0, self.zoom, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
		
		light0_pos = [20.0, 20.0, 20.0, 100.0]
		diffuse0 = [1.0, 1.0, 1.0, 1.0]
		specular0 = [0, 0, 0, 1.0]
		ambient0 = [0, 0, 0, 1.0]

		glLightfv(GL_LIGHT0, GL_POSITION, light0_pos)
		glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse0)
		glLightfv(GL_LIGHT0, GL_SPECULAR, specular0)
		glLightfv(GL_LIGHT0, GL_AMBIENT, ambient0)
		
		
		
		
		# Create a small white wire sphere in the 0 coordinate, just for refernece.
		glColor(1, 1, 1)
		glutWireSphere(0.1, 20, 20)
		
		glColor(1, 1, 1)
		glutWireSphere(1, 20, 20)
		
		for obj in self.sceneObjects:
			glPushMatrix()
			obj.render()
			glPopMatrix()
			
	def pickingObjects(self, x, y):
		
		buffer = glSelectBuffer(len(self.sceneObjects)*4)
		projection = glGetDoublev(GL_PROJECTION_MATRIX)
		viewport = glGetIntegerv(GL_VIEWPORT)
		
		glRenderMode(GL_SELECT)
		
		glMatrixMode(GL_PROJECTION)
		glPushMatrix()
		glLoadIdentity()
		gluPickMatrix(x, y, 15, 15, viewport)
		glMultMatrixf(projection)
		
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()
		glTranslate(0, 0, -3)
		glMultMatrixf(self.rotation)
		glInitNames()
		glPushName(0)
		
		for i in range(len(self.sceneObjects)):
			glPushMatrix()
			glLoadName(i)
			self.sceneObjects[i].render(True)
			glPopMatrix()
				
		glMatrixMode(GL_PROJECTION)
		glPopMatrix()
		glMatrixMode(GL_MODELVIEW)
		glFlush()
		
		glPopName()
			
		hits = glRenderMode(GL_RENDER)
		#print "Hits = (%d) %s " % (len(hits), hits)
		
		nearestHit = None
		for hit in hits:
			near, far, names = hit
			print near, far
			if (nearestHit == None) or (near < nearestHit[0]):
				nearestHit = [near, names[0]]
		
		if nearestHit != None:
			self.sceneObjects[nearestHit[1]].changeColor()
				
		self.updateGL()