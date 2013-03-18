# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'eqcatalogue_qgis/ui_dock.ui'
#
# Created: Mon Mar 18 15:58:43 2013
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dock(object):
    def setupUi(self, Dock):
        Dock.setObjectName(_fromUtf8("Dock"))
        Dock.resize(329, 544)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/inasafe/icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dock.setWindowIcon(icon)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setContentsMargins(3, 0, 3, 3)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.grpQuestion = QtGui.QGroupBox(self.dockWidgetContents)
        self.grpQuestion.setObjectName(_fromUtf8("grpQuestion"))
        self.gridLayout_3 = QtGui.QGridLayout(self.grpQuestion)
        self.gridLayout_3.setContentsMargins(0, 6, 0, 0)
        self.gridLayout_3.setVerticalSpacing(1)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.date_range = DateRangeFilter(self.grpQuestion)
        self.date_range.setObjectName(_fromUtf8("date_range"))
        self.gridLayout_3.addWidget(self.date_range, 11, 0, 1, 1)
        self.mrangeLabel = QtGui.QLabel(self.grpQuestion)
        self.mrangeLabel.setMargin(10)
        self.mrangeLabel.setObjectName(_fromUtf8("mrangeLabel"))
        self.gridLayout_3.addWidget(self.mrangeLabel, 8, 0, 1, 1)
        self.mscalesCombo = MultiCheckComboBox(self.grpQuestion)
        self.mscalesCombo.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        self.mscalesCombo.setObjectName(_fromUtf8("mscalesCombo"))
        self.gridLayout_3.addWidget(self.mscalesCombo, 7, 0, 1, 2)
        self.agenciesCombo = MultiCheckComboBox(self.grpQuestion)
        self.agenciesCombo.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        self.agenciesCombo.setObjectName(_fromUtf8("agenciesCombo"))
        self.gridLayout_3.addWidget(self.agenciesCombo, 4, 0, 1, 2)
        self.agencyLabel = QtGui.QLabel(self.grpQuestion)
        self.agencyLabel.setMargin(10)
        self.agencyLabel.setObjectName(_fromUtf8("agencyLabel"))
        self.gridLayout_3.addWidget(self.agencyLabel, 3, 0, 1, 1)
        self.mscalesLabel = QtGui.QLabel(self.grpQuestion)
        self.mscalesLabel.setMargin(10)
        self.mscalesLabel.setObjectName(_fromUtf8("mscalesLabel"))
        self.gridLayout_3.addWidget(self.mscalesLabel, 5, 0, 1, 1)
        self.drangeLabel = QtGui.QLabel(self.grpQuestion)
        self.drangeLabel.setMargin(10)
        self.drangeLabel.setObjectName(_fromUtf8("drangeLabel"))
        self.gridLayout_3.addWidget(self.drangeLabel, 10, 0, 1, 1)
        self.mag_range = DoubleRangeFilter(self.grpQuestion)
        self.mag_range.setObjectName(_fromUtf8("mag_range"))
        self.gridLayout_3.addWidget(self.mag_range, 9, 0, 1, 1)
        self.selectDbButton = QtGui.QToolButton(self.grpQuestion)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.selectDbButton.sizePolicy().hasHeightForWidth())
        self.selectDbButton.setSizePolicy(sizePolicy)
        self.selectDbButton.setObjectName(_fromUtf8("selectDbButton"))
        self.gridLayout_3.addWidget(self.selectDbButton, 2, 1, 1, 1)
        self.sdbLabel = QtGui.QLabel(self.grpQuestion)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sdbLabel.sizePolicy().hasHeightForWidth())
        self.sdbLabel.setSizePolicy(sizePolicy)
        self.sdbLabel.setMargin(10)
        self.sdbLabel.setObjectName(_fromUtf8("sdbLabel"))
        self.gridLayout_3.addWidget(self.sdbLabel, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.grpQuestion, 0, 0, 1, 1)
        self.filterButton = QtGui.QPushButton(self.dockWidgetContents)
        self.filterButton.setObjectName(_fromUtf8("filterButton"))
        self.gridLayout.addWidget(self.filterButton, 4, 0, 1, 1)
        Dock.setWidget(self.dockWidgetContents)
        self.mscalesLabel.setBuddy(self.mscalesCombo)

        self.retranslateUi(Dock)
        QtCore.QMetaObject.connectSlotsByName(Dock)

    def retranslateUi(self, Dock):
        Dock.setWindowTitle(QtGui.QApplication.translate("Dock", "Events Catalogue", None, QtGui.QApplication.UnicodeUTF8))
        self.grpQuestion.setTitle(QtGui.QApplication.translate("Dock", "Use criteria to filter the catalogue", None, QtGui.QApplication.UnicodeUTF8))
        self.mrangeLabel.setText(QtGui.QApplication.translate("Dock", "Define magnitude range:", None, QtGui.QApplication.UnicodeUTF8))
        self.agencyLabel.setText(QtGui.QApplication.translate("Dock", "Select one or more agencies:", None, QtGui.QApplication.UnicodeUTF8))
        self.mscalesLabel.setText(QtGui.QApplication.translate("Dock", "Select one or more magnitude scales:", None, QtGui.QApplication.UnicodeUTF8))
        self.drangeLabel.setText(QtGui.QApplication.translate("Dock", "Define date range:", None, QtGui.QApplication.UnicodeUTF8))
        self.selectDbButton.setText(QtGui.QApplication.translate("Dock", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.sdbLabel.setText(QtGui.QApplication.translate("Dock", "Select one db:", None, QtGui.QApplication.UnicodeUTF8))
        self.filterButton.setText(QtGui.QApplication.translate("Dock", "Filter", None, QtGui.QApplication.UnicodeUTF8))

from MultiCheckComboBox import MultiCheckComboBox
from rangeFilter import DoubleRangeFilter, DateRangeFilter
import resources_rc
