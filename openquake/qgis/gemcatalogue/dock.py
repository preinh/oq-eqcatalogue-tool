# -*- coding: utf-8 -*-

"""
"""
from PyQt4 import QtGui, QtCore

from ui_dock import Ui_Dock
from openquake.qgis.gemcatalogue.platform_settings \
    import PlatformSettingsDialog
from openquake.qgis.gemcatalogue import log_msg
from collections import namedtuple
from extentSelector import ExtentSelector

Range = namedtuple('Range', 'low_value high_value')


class Dock(QtGui.QDockWidget, Ui_Dock):
    def __init__(self, iface, gemcatalogue, parent=None):
        QtGui.QDockWidget.__init__(self, parent)
        self.iface = iface
        self.gemcatalogue = gemcatalogue
        self.setupUi(self)
        self.add_range_sliders()
        self.canvas = self.iface.mapCanvas()

        self.extentSelector = ExtentSelector()
        self.extentSelector.setCanvas(self.canvas)

        self.connect(self.extentSelector, QtCore.SIGNAL("rectangleCreated"),
                     self.polygonCreated)

    def closeEvent(self, event):
        self.emit(QtCore.SIGNAL("closed"), self)
        return QtGui.QDockWidget.closeEvent(self, event)

    def enableBusyCursor(self):
        """Set the hourglass enabled and stop listening for layer changes."""
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

    def disableBusyCursor(self):
        """Disable the hourglass cursor and listen for layer changes."""
        QtGui.qApp.restoreOverrideCursor()

    def add_range_sliders(self):
        self.mag_range.setOrientation(QtCore.Qt.Horizontal)
        self.mag_range.setMinimum(1)
        self.mag_range.setMaximum(10)
        self.mag_range.setLowValue(5)
        self.mag_range.setHighValue(8)

        self.date_range.setOrientation(QtCore.Qt.Horizontal)
        self.date_range.setMinimum(QtCore.QDate(1970, 01, 01))
        self.date_range.setMaximum(QtCore.QDate.currentDate())
        self.date_range.setLowValue(QtCore.QDate(1970, 01, 01))
        self.date_range.setHighValue(QtCore.QDate.currentDate())

    def update_selectDbComboBox(self, db_sel):
        if db_sel is not None and db_sel != '':
            if self.selectDbComboBox.count() == 0:
                self.selectDbComboBox.addItem(db_sel)
                self.gemcatalogue.load_countries()
            else:
                item_index = self.selectDbComboBox.findText(db_sel)
                self.selectDbComboBox.blockSignals(True)
                # Elem not in list.
                if item_index != -1:
                    self.selectDbComboBox.removeItem(item_index)

                self.selectDbComboBox.insertItem(0, db_sel)
                self.selectDbComboBox.blockSignals(False)
                self.selectDbComboBox.setCurrentIndex(0)

    @QtCore.pyqtSlot()
    def on_addDbBtn_clicked(self):
        db_sel = unicode(QtGui.QFileDialog.getOpenFileName(
            self.iface.mainWindow(), 'Choose db',
            QtCore.QDir.homePath(),
            "Catalogue db file (*.db);;All files (*.*)"))
        self.update_selectDbComboBox(db_sel)

    @QtCore.pyqtSlot()
    def on_filterBtn_clicked(self):
        agencies_selected = self.agenciesComboBox.checkedItems()
        mscales_selected = self.mscalesComboBox.checkedItems()
        mvalues_selected = Range(self.mag_range.lowValue(),
                                 self.mag_range.highValue())
        dvalues_selected = ((self.date_range.lowValue()).toPyDateTime(),
                            (self.date_range.highValue()).toPyDateTime())

        self.gemcatalogue.update_map(agencies_selected, mscales_selected,
                                     mvalues_selected, dvalues_selected)

    @QtCore.pyqtSlot()
    def on_downloadBtn_clicked(self):
        qs = QtCore.QSettings()
        hostname = qs.value('gemcatalogue/hostname', '')
        username = qs.value('gemcatalogue/username', '')
        password = qs.value('gemcatalogue/password', '')
        if not (hostname and username and password):
            dialog = PlatformSettingsDialog(self.iface)
            if dialog.exec_():
                self.gemcatalogue.show_exposure(hostname, username, password)
        else:
            self.gemcatalogue.show_exposure(hostname, username, password)

    @QtCore.pyqtSlot(str)
    def on_selectDbComboBox_currentIndexChanged(self, selectedDb):
        self.gemcatalogue.update_catalogue_db(selectedDb)

    def set_agencies(self, agencies):
        self.agenciesComboBox.clear()
        self.agenciesComboBox.addItems(agencies)
        self.agenciesComboBox.checkAll(True)

    def set_magnitude_scales(self, magnitude_scales):
        self.mscalesComboBox.clear()
        self.mscalesComboBox.addItems(magnitude_scales)
        self.mscalesComboBox.checkAll(True)

    @QtCore.pyqtSlot()
    def on_drawBtn_clicked(self):
        self.hasValidGeoFilter = False
        self.extentSelector.start()
        self.extentSelector.getExtent()

    @QtCore.pyqtSlot()
    def on_clearBtn_clicked(self):
        self.extentSelector.stop()

    def polygonCreated(self):
        self.hasValidGeoFilter = True
        log_msg(self.hasValidGeoFilter)
        self.extentSelector.show()

    def selectedExtent(self):
        return self.extentSelector.getExtent()