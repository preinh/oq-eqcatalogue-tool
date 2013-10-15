# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dock.ui'
#
# Created: Tue Oct 15 00:45:45 2013
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dock(object):
    def setupUi(self, Dock):
        Dock.setObjectName(_fromUtf8("Dock"))
        Dock.resize(454, 689)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/inasafe/icon.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dock.setWindowIcon(icon)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setContentsMargins(3, 0, 3, 3)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.dbGrb = QtGui.QGroupBox(self.dockWidgetContents)
        self.dbGrb.setObjectName(_fromUtf8("dbGrb"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.dbGrb)
        self.verticalLayout_2.setContentsMargins(0, 6, 0, 0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(-1, 10, -1, -1)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.selectDbComboBox = QtGui.QComboBox(self.dbGrb)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.selectDbComboBox.sizePolicy().hasHeightForWidth())
        self.selectDbComboBox.setSizePolicy(sizePolicy)
        self.selectDbComboBox.setObjectName(_fromUtf8("selectDbComboBox"))
        self.horizontalLayout_3.addWidget(self.selectDbComboBox)
        self.addDbBtn = QtGui.QToolButton(self.dbGrb)
        self.addDbBtn.setObjectName(_fromUtf8("addDbBtn"))
        self.horizontalLayout_3.addWidget(self.addDbBtn)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.verticalLayout.addWidget(self.dbGrb)
        self.magnitudeGrb = QtGui.QGroupBox(self.dockWidgetContents)
        self.magnitudeGrb.setObjectName(_fromUtf8("magnitudeGrb"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.magnitudeGrb)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.mag_range = DoubleRangeFilter(self.magnitudeGrb)
        self.mag_range.setObjectName(_fromUtf8("mag_range"))
        self.verticalLayout_4.addWidget(self.mag_range)
        self.verticalLayout.addWidget(self.magnitudeGrb)
        self.actionsBtns = QtGui.QVBoxLayout()
        self.actionsBtns.setContentsMargins(-1, 0, -1, -1)
        self.actionsBtns.setObjectName(_fromUtf8("actionsBtns"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.drawBtn = QtGui.QPushButton(self.dockWidgetContents)
        self.drawBtn.setObjectName(_fromUtf8("drawBtn"))
        self.horizontalLayout.addWidget(self.drawBtn)
        self.clearBtn = QtGui.QPushButton(self.dockWidgetContents)
        self.clearBtn.setObjectName(_fromUtf8("clearBtn"))
        self.horizontalLayout.addWidget(self.clearBtn)
        self.actionsBtns.addLayout(self.horizontalLayout)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.filterBtn = QtGui.QPushButton(self.dockWidgetContents)
        self.filterBtn.setEnabled(True)
        self.filterBtn.setObjectName(_fromUtf8("filterBtn"))
        self.horizontalLayout_4.addWidget(self.filterBtn)
        self.downloadBtn = QtGui.QPushButton(self.dockWidgetContents)
        self.downloadBtn.setEnabled(False)
        self.downloadBtn.setObjectName(_fromUtf8("downloadBtn"))
        self.horizontalLayout_4.addWidget(self.downloadBtn)
        self.actionsBtns.addLayout(self.horizontalLayout_4)
        self.verticalLayout.addLayout(self.actionsBtns)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        Dock.setWidget(self.dockWidgetContents)

        self.retranslateUi(Dock)
        QtCore.QMetaObject.connectSlotsByName(Dock)

    def retranslateUi(self, Dock):
        Dock.setWindowTitle(_translate("Dock", "Events Catalogue", None))
        self.dbGrb.setTitle(_translate("Dock", "Select one of the availables db", None))
        self.addDbBtn.setText(_translate("Dock", "...", None))
        self.magnitudeGrb.setTitle(_translate("Dock", "Define magnitude range", None))
        self.drawBtn.setText(_translate("Dock", "Draw", None))
        self.clearBtn.setText(_translate("Dock", "Clear", None))
        self.filterBtn.setText(_translate("Dock", "Filter", None))
        self.downloadBtn.setText(_translate("Dock", "Download", None))

from rangeFilter import DoubleRangeFilter
import resources_rc
