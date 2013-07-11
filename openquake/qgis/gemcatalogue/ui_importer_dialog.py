# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_importer_dialog.ui'
#
# Created: Thu Jul 11 12:37:51 2013
#      by: PyQt4 UI code generator 4.9.3
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
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.selectCatalogueLineEdit = QtGui.QLineEdit(ImporterDialog)
        self.selectCatalogueLineEdit.setReadOnly(True)
        self.selectCatalogueLineEdit.setObjectName(_fromUtf8("selectCatalogueLineEdit"))
        self.horizontalLayout_3.addWidget(self.selectCatalogueLineEdit)
        self.cataloguefileSelBtn = QtGui.QToolButton(ImporterDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cataloguefileSelBtn.sizePolicy().hasHeightForWidth())
        self.cataloguefileSelBtn.setSizePolicy(sizePolicy)
        self.cataloguefileSelBtn.setObjectName(_fromUtf8("cataloguefileSelBtn"))
        self.horizontalLayout_3.addWidget(self.cataloguefileSelBtn)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.spatialiteDbLabel = QtGui.QLabel(ImporterDialog)
        self.spatialiteDbLabel.setObjectName(_fromUtf8("spatialiteDbLabel"))
        self.verticalLayout.addWidget(self.spatialiteDbLabel)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.selectDbLineEdit = QtGui.QLineEdit(ImporterDialog)
        self.selectDbLineEdit.setReadOnly(True)
        self.selectDbLineEdit.setObjectName(_fromUtf8("selectDbLineEdit"))
        self.horizontalLayout.addWidget(self.selectDbLineEdit)
        self.dbNameBtn = QtGui.QToolButton(ImporterDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dbNameBtn.sizePolicy().hasHeightForWidth())
        self.dbNameBtn.setSizePolicy(sizePolicy)
        self.dbNameBtn.setObjectName(_fromUtf8("dbNameBtn"))
        self.horizontalLayout.addWidget(self.dbNameBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.cancelBtn = QtGui.QPushButton(ImporterDialog)
        self.cancelBtn.setEnabled(True)
        self.cancelBtn.setObjectName(_fromUtf8("cancelBtn"))
        self.horizontalLayout_2.addWidget(self.cancelBtn)
        self.importBtn = QtGui.QPushButton(ImporterDialog)
        self.importBtn.setEnabled(False)
        self.importBtn.setObjectName(_fromUtf8("importBtn"))
        self.horizontalLayout_2.addWidget(self.importBtn)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(ImporterDialog)
        QtCore.QObject.connect(self.cancelBtn, QtCore.SIGNAL(_fromUtf8("clicked()")), ImporterDialog.reject)
        QtCore.QObject.connect(self.importBtn, QtCore.SIGNAL(_fromUtf8("clicked()")), ImporterDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(ImporterDialog)

    def retranslateUi(self, ImporterDialog):
        ImporterDialog.setWindowTitle(QtGui.QApplication.translate("ImporterDialog", "Import catalogue file", None, QtGui.QApplication.UnicodeUTF8))
        self.selCatalogueFileLabel.setText(QtGui.QApplication.translate("ImporterDialog", "Select catalogue file:", None, QtGui.QApplication.UnicodeUTF8))
        self.cataloguefileSelBtn.setText(QtGui.QApplication.translate("ImporterDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.spatialiteDbLabel.setText(QtGui.QApplication.translate("ImporterDialog", "Spatialite db name:", None, QtGui.QApplication.UnicodeUTF8))
        self.dbNameBtn.setText(QtGui.QApplication.translate("ImporterDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelBtn.setText(QtGui.QApplication.translate("ImporterDialog", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.importBtn.setText(QtGui.QApplication.translate("ImporterDialog", "&Import", None, QtGui.QApplication.UnicodeUTF8))

