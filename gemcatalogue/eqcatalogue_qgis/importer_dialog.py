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
        self.iface = iface
        self.setupUi(self)
        self.file_filter = 'Isf file (*.txt *.html)' + ';; Iaspei file (*.csv)'
        self.import_file_path = None
        self.save_file_path = None
        self.selectCatalogueLineEdit.textChanged.connect(self.toggle_import_btn)
        self.selectDbLineEdit.textChanged.connect(self.toggle_import_btn)

    @pyqtSlot()    
    def on_cataloguefileSelBtn_clicked(self):
        dialog = QFileDialog(self, 'Select Catalogue file')
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter(self.file_filter)
        dialog.setViewMode(QFileDialog.List)
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        if dialog.exec_():
            self.import_file_path = dialog.selectedFiles()[0]
        self.selectCatalogueLineEdit.setText(self.import_file_path)
        self.fmt = dialog.selectedNameFilter()

    @pyqtSlot()
    def on_dbNameBtn_clicked(self):
        self.save_file_path = unicode(QFileDialog.getSaveFileName(
            self.iface.mainWindow(), 'Save Catalogue file into',
            QDir.homePath()))
        self.selectDbLineEdit.setText(self.save_file_path)        

    def toggle_import_btn(self):
        if (self.import_file_path is not None and
            self.save_file_path is not None):
            self.importBtn.setEnabled(True)
        else:
            self.importBtn.setEnabled(False)

    def select_db(self):
        pass
        

    def closeEvent(self, event):
        self.emit( SIGNAL( "closed" ), self )
        return QDialog.closeEvent(self, event)
	
