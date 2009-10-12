from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_help_dialog import *

class HelpDialog(QDialog, Ui_Dialog):
    """
    The help dialog of Joaquim.
    """

    def __init__(self, parent=None):
        """
        Constructor.
        """
        
        super(HelpDialog, self).__init__(parent)
        self.setupUi(self)