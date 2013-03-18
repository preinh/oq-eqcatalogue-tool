# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'eqcatalogue_qgis/ui_importer_dialog.ui'
#
# Created: Mon Mar 18 15:49:15 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ImporterDialog(object):
    def setupUi(self, ImporterDialog):
        ImporterDialog.setObjectName(_fromUtf8("ImporterDialog"))
        ImporterDialog.resize(285, 179)
        self.verticalLayout = QtGui.QVBoxLayout(ImporterDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.selCatalogueFileLabel = QtGui.QLabel(ImporterDialog)
        self.selCatalogueFileLabel.setObjectName(_fromUtf8("selCatalogueFileLabel"))
        self.verticalLayout.addWidget(self.selCatalogueFileLabel)
        self.cataloguefileSelBtn = QtGui.QToolButton(ImporterDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cataloguefileSelBtn.sizePolicy().hasHeightForWidth())
        self.cataloguefileSelBtn.setSizePolicy(sizePolicy)
        self.cataloguefileSelBtn.setObjectName(_fromUtf8("cataloguefileSelBtn"))
        self.verticalLayout.addWidget(self.cataloguefileSelBtn)
        self.spatialiteDbLabel = QtGui.QLabel(ImporterDialog)
        self.spatialiteDbLabel.setObjectName(_fromUtf8("spatialiteDbLabel"))
        self.verticalLayout.addWidget(self.spatialiteDbLabel)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.availableDbCombo = QtGui.QComboBox(ImporterDialog)
        self.availableDbCombo.setObjectName(_fromUtf8("availableDbCombo"))
        self.horizontalLayout.addWidget(self.availableDbCombo)
        self.dbNameBtn = QtGui.QToolButton(ImporterDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dbNameBtn.sizePolicy().hasHeightForWidth())
        self.dbNameBtn.setSizePolicy(sizePolicy)
        self.dbNameBtn.setObjectName(_fromUtf8("dbNameBtn"))
        self.horizontalLayout.addWidget(self.dbNameBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(ImporterDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ImporterDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ImporterDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ImporterDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ImporterDialog)

    def retranslateUi(self, ImporterDialog):
        ImporterDialog.setWindowTitle(QtGui.QApplication.translate("ImporterDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.selCatalogueFileLabel.setText(QtGui.QApplication.translate("ImporterDialog", "Select catalogue file:", None, QtGui.QApplication.UnicodeUTF8))
        self.cataloguefileSelBtn.setText(QtGui.QApplication.translate("ImporterDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.spatialiteDbLabel.setText(QtGui.QApplication.translate("ImporterDialog", "Spatialite db name:", None, QtGui.QApplication.UnicodeUTF8))
        self.dbNameBtn.setText(QtGui.QApplication.translate("ImporterDialog", "...", None, QtGui.QApplication.UnicodeUTF8))

