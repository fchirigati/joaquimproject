from PyQt4.QtOpenGL import *
from PyQt4.QtGui import *
from PyQt4 import QtCore
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from objects import *

class GlWidget(QGLWidget):
	"""Our implementation of QGLWidget widget. :) - Joaquim, el gato."""
	
	def __init__ (self, parent=None):
		"""Constructor"""
		
		super(GlWidget, self).__init__(parent)
		#Para que o movimento do mouse seja reconhecido sem se pressionar nenhum botao do mouse
		self.setMouseTracking(True)
		
		self.sceneObjects = []
		self.selectedObject = None
		self.mousePosX = 0.0
		self.mousePosY = 0.0
		self.mousePosZ = 0.0
		self.move = 0.0
		self.z = 0.0
		self.zoom = 2.0
		self.applyZoom = 0
		
		
	def paintGL(self):
		"""A Simple drawing callback for drawing one triangle"""
		
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		self.render()

	def resizeGL (self, width, height):
		"""A simple resize callback."""
		
		side = min(width,height)
		glViewport((width - side) / 2, (height - side) / 2, side, side)
		glMatrixMode(GL_MODELVIEW)
		#glLoadIdentity()
		#gluLookAt (0.0, 0.0, self.zoom, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
		self.updateGL()

	def mouseMoveEvent(self, ev):
		self.updateMousePosition()
		if self.applyZoom:
			if self.z > self.zoom:
				self.zoom-=abs(self.zoom - self.z)/500
				glLoadIdentity()
				gluLookAt (self.move, 0.0, self.zoom, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
				self.updateGL()
			else:
				self.zoom+=abs(self.zoom - self.z)/500
				glLoadIdentity()
				gluLookAt (self.move, 0.0, self.zoom, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
				self.updateGL() 
		self.update()
		
	def mousePressEvent(self, ev):
		print "Clico! ;D"
		self.pickingObjects(self.mousePosX, self.mousePosY)
		if ev.button() == QtCore.Qt.RightButton:
			self.applyZoom = 1
			self.z = self.mousePosY
#		
	def mouseReleaseEvent(self, ev):
		print "Solto... :("
		if ev.button() == QtCore.Qt.RightButton:
			self.applyZoom = 0		 

	def enterEvent(self, ev):
		self.setFocus()
		self.grabKeyboard()
		
	def leaveEvent(self, ev):
		self.parent().setFocus()
		self.releaseKeyboard()

	def keyPressEvent(self, ev):
		key = str(ev.text()).upper()
		if (key == "C"):
			newCube = Cube(0.5, False)
			newCube.setCentralPosition(self.getMouseScenePosition())
			self.sceneObjects.append(newCube)
			self.update()
		elif (key == "E"):
			newSphere = Sphere(0.5, False)
			newSphere.setCentralPosition(self.getMouseScenePosition())
			self.sceneObjects.append(newSphere)
			self.update()
		elif (key == "W"):
			self.zoom-=0.2
			glLoadIdentity()
			gluLookAt (self.move, 0.0, self.zoom, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
			self.updateGL()
		elif (key == "S"):
			self.zoom+=0.2
			glLoadIdentity()
			gluLookAt (self.move, 0.0, self.zoom, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
			self.updateGL()
		elif (key == "A"):
			self.move-=0.3
			glLoadIdentity()
			gluLookAt (self.move, 0.0, self.zoom, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
			self.updateGL()
		elif (key == "D"):
			self.move+=0.3
			glLoadIdentity()
			gluLookAt (self.move, 0.0, self.zoom, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
			self.updateGL()
		else:
			pass
		
	def updateMousePosition(self):
		self.mousePosX = self.mapFromGlobal(QCursor.pos()).x()
		self.mousePosY = self.mapFromGlobal(QCursor.pos()).y()
			
	def getMouseScenePosition(self):
#		self.mousePosZ = glReadPixels(self.mousePosX, self.mousePosY, 1, 1,
#									  GL_DEPTH_COMPONENT, GL_FLOAT)
		self.mousePosZ = 0.1

		adjustedY = glGetIntegerv(GL_VIEWPORT)[3] - self.mousePosY - 1
		
		self.coordPosition = gluUnProject(self.mousePosX, adjustedY, self.mousePosZ,
										  glGetDoublev(GL_MODELVIEW_MATRIX),
										  glGetDoublev(GL_PROJECTION_MATRIX),
										  glGetIntegerv(GL_VIEWPORT))
		
		return self.coordPosition
		
	def render(self):
		
		glMatrixMode(GL_MODELVIEW)
		
		glEnable(GL_LIGHTING)
		glEnable(GL_LIGHT0)
		glEnable(GL_COLOR_MATERIAL)
		
		light0_pos = 40.0, 0.0, 0.0, 100.0
		diffuse0 = 1.0, 1.0, 1.0, 1.0
		specular0 = 0, 0, 0, 1.0
		ambient0 = 0, 0, 0, 1.0

		glMatrixMode(GL_MODELVIEW)
		glLightfv(GL_LIGHT0, GL_POSITION, light0_pos)
		glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse0)
		glLightfv(GL_LIGHT0, GL_SPECULAR, specular0)
		glLightfv(GL_LIGHT0, GL_AMBIENT, ambient0)
		
		for obj in self.sceneObjects:
			glPushMatrix()
			obj.render()
			glPopMatrix()

		glLoadIdentity()
		gluLookAt (self.move, 0.0, self.zoom, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
			
	def pickingObjects(self, x, y):
		buffer = glSelectBuffer(len(self.sceneObjects)*4)
		
		glRenderMode(GL_SELECT)
		
		glMatrixMode(GL_PROJECTION)
		glPushMatrix()
		glLoadIdentity()
		
		projection = glGetDoublev(GL_PROJECTION_MATRIX)
		viewport = glGetIntegerv(GL_VIEWPORT)
		
		print "X =", x
		print "Y =", viewport[3] - y - 1
		
		gluPickMatrix(x, viewport[3] - y - 1, 1500, 1500, viewport)
		glMultMatrixf(projection)
		
		glInitNames()
		glPushName(0)
		
		for i in range(len(self.sceneObjects)):
			print "LoadName =", i+1
			print "SceneObject =", self.sceneObjects[i]
			glLoadName(i)
			self.sceneObjects[i].render(False)
			
		glMatrixMode(GL_PROJECTION)
		glPopMatrix()
		glFlush()
			
		hits = glRenderMode(GL_RENDER)
		print "Hits = (%d) %s " % (len(hits), hits)
		object = [0, 0]
		for hit in hits:
			near, far, names = hit
			print "Near =", near
			print "Far =", far
			print "Names =", names
			if (object[0] < far):
				object = [far, names[0]]
		print "Object =", object
		
		glPopName()
		
		for obj in self.sceneObjects:
			if ((self.sceneObjects.index(obj)+1)==object[1]):
				print "Selected!"
				obj.selected = True
				obj.changeColor()
			else:
				print "Not Selected!"
				
		self.updateGL()