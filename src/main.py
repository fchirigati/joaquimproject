from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui.mainwindow import MainWindow
import sys

app = QApplication(sys.argv)
form = MainWindow()
form.show()
app.exec_()
