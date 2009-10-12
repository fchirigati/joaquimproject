from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_about_dialog import *

class AboutDialog(QDialog, Ui_Dialog):
    """
    The about dialog of Joaquim.
    """

    def __init__(self, parent=None):
        """
        Constructor.
        """
        
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)