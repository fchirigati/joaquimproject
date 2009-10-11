from PyQt4.QtCore import *
from PyQt4.QtGui import *
from OpenGL.GLUT import glutInit
from ui.mainwindow import MainWindow
import sys

app = QApplication(sys.argv)
form = MainWindow()
glutInit(sys.argv)
form.show()
app.exec_()
