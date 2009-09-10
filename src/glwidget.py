from PyQt4.QtOpenGL import *
from PyQt4.QtGui import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.raw.GLUT import glutWireCube, glutWireSphere

class GlWidget(QGLWidget):
	"""Our implementation of QGLWidget widget. :) - Joaquim, el gato."""
	
	def __init__ (self, parent=None):
		"""Constructor."""
		super(GlWidget, self).__init__(parent)
		self.esfera = False
		self.cubinho = False
		
	def paintGL(self):
		"""A Simple drawing callback for drawing one triangle"""
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glRotate(2, 0.5, 0.9, 0.5)
		if (self.esfera):
			glColor3f(1.0, 0, 0)
			glutWireSphere(0.5, 40, 20) #RENAN, volte para casa, Renan...
		if (self.cubinho):
			glColor3f(1.0, 0, 1.0)
			glutWireCube(0.5)

	def resizeGL (self, width, height):
		"""A simple resize callback."""
		side = min(width,height)
		glViewport((width - side) / 2, (height - side) / 2, side, side)
#		glMatrixMode(GL_PROJECTION)
#		glLoadIdentity()
#		gluPerspective(60, width/height, 1.0, 100.0)
		glMatrixMode(GL_MODELVIEW)
#		glLoadIdentity()
#		glTranslatef(-0.5, -0.5, 0)
#		glRotate(45, 0, 0, -1.0)

	def mouseMoveEvent(self, ev):
		print "Moh-vel"
		
	def mousePressEvent(self, ev):
		print "Clico! :D"
		
	def mouseReleaseEvent(self, ev):
		print "Solto... :(" 			

	def enterEvent(self, ev):
		self.setFocus()
		self.grabKeyboard()
		
	def leaveEvent(self, ev):
		self.parent().setFocus()
		self.releaseKeyboard()

	def keyPressEvent(self, ev):
		#ctrl, shift = self._GetCtrlShift(ev)
		key = str(ev.text()).upper()
		if (key == "C"):
			self.cubinho = not self.cubinho
			self.update()
		elif (key == "E"):
			self.esfera = not self.esfera
			self.update()
		elif (key == "R"):
			self.update()
			print QCursor.pos()