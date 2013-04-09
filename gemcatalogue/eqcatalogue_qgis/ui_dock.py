# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'eqcatalogue_qgis/ui_dock.ui'
#
# Created: Thu Mar 21 11:07:53 2013
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
        Dock.resize(435, 508)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/inasafe/icon.png")),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dock.setWindowIcon(icon)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setContentsMargins(3, 0, 3, 3)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.grpQuestion = QtGui.QGroupBox(self.dockWidgetContents)
        self.grpQuestion.setObjectName(_fromUtf8("grpQuestion"))
        self.gridLayout_3 = QtGui.QGridLayout(self.grpQuestion)
        self.gridLayout_3.setContentsMargins(0, 6, 0, 0)
        self.gridLayout_3.setVerticalSpacing(1)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.date_range = DateRangeFilter(self.grpQuestion)
        self.date_range.setObjectName(_fromUtf8("date_range"))
        self.gridLayout_3.addWidget(self.date_range, 15, 0, 1, 1)
        self.mrangeLabel = QtGui.QLabel(self.grpQuestion)
        self.mrangeLabel.setMargin(10)
        self.mrangeLabel.setObjectName(_fromUtf8("mrangeLabel"))
        self.gridLayout_3.addWidget(self.mrangeLabel, 12, 0, 1, 1)
        self.mscalesComboBox = MultiCheckComboBox(self.grpQuestion)
        self.mscalesComboBox.setInsertPolicy(
            QtGui.QComboBox.InsertAlphabetically)
        self.mscalesComboBox.setObjectName(_fromUtf8("mscalesComboBox"))
        self.gridLayout_3.addWidget(self.mscalesComboBox, 11, 0, 1, 2)
        self.agenciesComboBox = MultiCheckComboBox(self.grpQuestion)
        self.agenciesComboBox.setInsertPolicy(
            QtGui.QComboBox.InsertAlphabetically)
        self.agenciesComboBox.setObjectName(_fromUtf8("agenciesComboBox"))
        self.gridLayout_3.addWidget(self.agenciesComboBox, 8, 0, 1, 2)
        self.agencyLabel = QtGui.QLabel(self.grpQuestion)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum,
                                       QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.agencyLabel.sizePolicy().hasHeightForWidth())
        self.agencyLabel.setSizePolicy(sizePolicy)
        self.agencyLabel.setMargin(10)
        self.agencyLabel.setObjectName(_fromUtf8("agencyLabel"))
        self.gridLayout_3.addWidget(self.agencyLabel, 7, 0, 1, 1)
        self.mscalesLabel = QtGui.QLabel(self.grpQuestion)
        self.mscalesLabel.setMargin(10)
        self.mscalesLabel.setObjectName(_fromUtf8("mscalesLabel"))
        self.gridLayout_3.addWidget(self.mscalesLabel, 9, 0, 1, 1)
        self.drangeLabel = QtGui.QLabel(self.grpQuestion)
        self.drangeLabel.setMargin(10)
        self.drangeLabel.setObjectName(_fromUtf8("drangeLabel"))
        self.gridLayout_3.addWidget(self.drangeLabel, 14, 0, 1, 1)
        self.mag_range = DoubleRangeFilter(self.grpQuestion)
        self.mag_range.setObjectName(_fromUtf8("mag_range"))
        self.gridLayout_3.addWidget(self.mag_range, 13, 0, 1, 1)
        self.label = QtGui.QLabel(self.grpQuestion)
        self.label.setMargin(10)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_3.addWidget(self.label, 4, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(-1, 10, -1, -1)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.selectDbComboBox = QtGui.QComboBox(self.grpQuestion)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
                                       QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.selectDbComboBox.sizePolicy().hasHeightForWidth())
        self.selectDbComboBox.setSizePolicy(sizePolicy)
        self.selectDbComboBox.setObjectName(_fromUtf8("selectDbComboBox"))
        self.horizontalLayout_3.addWidget(self.selectDbComboBox)
        self.addDbBtn = QtGui.QToolButton(self.grpQuestion)
        self.addDbBtn.setObjectName(_fromUtf8("addDbBtn"))
        self.horizontalLayout_3.addWidget(self.addDbBtn)
        self.gridLayout_3.addLayout(self.horizontalLayout_3, 5, 0, 1, 2)
        self.gridLayout.addWidget(self.grpQuestion, 0, 0, 1, 1)
        self.filterBtn = QtGui.QPushButton(self.dockWidgetContents)
        self.filterBtn.setEnabled(True)
        self.filterBtn.setObjectName(_fromUtf8("filterBtn"))
        self.gridLayout.addWidget(self.filterBtn, 5, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum,
                                       QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 6, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 10, -1, -1)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.drawBtn = QtGui.QPushButton(self.dockWidgetContents)
        self.drawBtn.setObjectName(_fromUtf8("drawBtn"))
        self.horizontalLayout.addWidget(self.drawBtn)
        self.clearBtn = QtGui.QPushButton(self.dockWidgetContents)
        self.clearBtn.setObjectName(_fromUtf8("clearBtn"))
        self.horizontalLayout.addWidget(self.clearBtn)
        self.gridLayout.addLayout(self.horizontalLayout, 4, 0, 1, 1)
        Dock.setWidget(self.dockWidgetContents)
        self.mscalesLabel.setBuddy(self.mscalesComboBox)

        self.retranslateUi(Dock)
        QtCore.QMetaObject.connectSlotsByName(Dock)

    def retranslateUi(self, Dock):
        Dock.setWindowTitle(
            QtGui.QApplication.translate("Dock", "Events Catalogue", None,
                                         QtGui.QApplication.UnicodeUTF8))
        self.grpQuestion.setTitle(QtGui.QApplication.translate("Dock",
                                                               "Use criteria to filter the catalogue",
                                                               None,
                                                               QtGui.QApplication.UnicodeUTF8))
        self.mrangeLabel.setText(
            QtGui.QApplication.translate("Dock", "Define magnitude range:",
                                         None, QtGui.QApplication.UnicodeUTF8))
        self.agencyLabel.setText(
            QtGui.QApplication.translate("Dock", "Select one or more agencies:",
                                         None, QtGui.QApplication.UnicodeUTF8))
        self.mscalesLabel.setText(QtGui.QApplication.translate("Dock",
                                                               "Select one or more magnitude scales:",
                                                               None,
                                                               QtGui.QApplication.UnicodeUTF8))
        self.drangeLabel.setText(
            QtGui.QApplication.translate("Dock", "Define date range:", None,
                                         QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dock",
                                                        "Select one of the availables db:",
                                                        None,
                                                        QtGui.QApplication.UnicodeUTF8))
        self.addDbBtn.setText(QtGui.QApplication.translate("Dock", "...", None,
                                                           QtGui.QApplication.UnicodeUTF8))
        self.filterBtn.setText(
            QtGui.QApplication.translate("Dock", "Filter", None,
                                         QtGui.QApplication.UnicodeUTF8))
        self.drawBtn.setText(QtGui.QApplication.translate("Dock", "Draw", None,
                                                          QtGui.QApplication.UnicodeUTF8))
        self.clearBtn.setText(
            QtGui.QApplication.translate("Dock", "Clear", None,
                                         QtGui.QApplication.UnicodeUTF8))


from MultiCheckComboBox import MultiCheckComboBox
from rangeFilter import DoubleRangeFilter, DateRangeFilter
import resources_rc
