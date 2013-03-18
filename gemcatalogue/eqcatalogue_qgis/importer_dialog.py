# -*- coding: utf-8 -*-

"""
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from ui_importer_dialog import Ui_ImporterDialog


class ImporterDialog(QDialog, Ui_ImporterDialog):
    def __init__(self, iface, parent=None):
        QDialog.__init__(self)
        self.setupUi(self)

    def closeEvent(self, event):
        self.emit( SIGNAL( "closed" ), self )
        return QDialog.closeEvent(self, event)
	
