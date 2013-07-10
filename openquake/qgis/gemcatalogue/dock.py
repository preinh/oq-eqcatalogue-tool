# -*- coding: utf-8 -*-

"""
"""
from PyQt4 import QtGui, QtCore

from ui_dock import Ui_Dock
from openquake.qgis.gemcatalogue.platform_settings \
    import PlatformSettingsDialog
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
        self.extentSelector = ExtentSelector(self.canvas)

        self.extentSelector.tool.rectangleCreated.connect(self.polygonCreated)

    def closeEvent(self, event):
        self.emit(QtCore.SIGNAL("closed()"), self)
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
        agencies_selected = self.get_selected_items(self.agenciesListSelector)
        mscales_selected = self.mscalesComboBox.checkedItems()
        mvalues_selected = Range(self.mag_range.lowValue(),
                                 self.mag_range.highValue())
        dvalues_selected = (self.minDateDe.dateTime().toPyDateTime(),
                            self.maxDateDe.dateTime().toPyDateTime())

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
        self.add_items(self.agenciesListSelector, selected=agencies)

    def set_magnitude_scales(self, magnitude_scales):
        self.mscalesComboBox.clear()
        self.mscalesComboBox.addItems(magnitude_scales)
        self.mscalesComboBox.checkAll(True)

    def set_dates(self, dates):
        min_date, max_date = dates
        self.minDateDe.setDateTimeRange(
            QtCore.QDateTime(min_date), QtCore.QDateTime(max_date))
        self.maxDateDe.setDateTimeRange(
            QtCore.QDateTime(min_date), QtCore.QDateTime(max_date))
        self.minDateDe.setDateTime(QtCore.QDateTime(min_date))
        self.maxDateDe.setDateTime(QtCore.QDateTime(max_date))

    @QtCore.pyqtSlot()
    def on_drawBtn_clicked(self):
        self.extentSelector.start()
        self.extentSelector.getExtent()

    @QtCore.pyqtSlot()
    def on_clearBtn_clicked(self):
        self.extentSelector.stop()
        self.downloadBtn.setEnabled(False)

    def polygonCreated(self):
        self.downloadBtn.setEnabled(True)

    def selectedExtent(self):
        return self.extentSelector.getExtent()

    #START LIST BUILDER
    def get_selected_items(self, selector):
        selectedList, _ = self._get_lists(selector)
        for i in range(selectedList.count()):
            yield selectedList.item(i).text()

    def add_items(self, selector, selected=None, unselected=None):
        selectedList, unselectedList = self._get_lists(selector)
        if selected is not None:
            selectedList.addItems(selected)
        if unselected is not None:
            unselectedList.addItems(unselected)

    @QtCore.pyqtSlot()
    def on_selectAllAgencies_clicked(self):
        self._select_all(self.agenciesListSelector)

    @QtCore.pyqtSlot()
    def on_deselectAllAgencies_clicked(self):
        self._deselect_all(self.agenciesListSelector)

    @QtCore.pyqtSlot()
    def on_selectAgencies_clicked(self):
        self._select(self.agenciesListSelector)

    @QtCore.pyqtSlot()
    def on_deselectAgencies_clicked(self):
        self._deselect(self.agenciesListSelector)

    def _select_all(self, selector):
        selectedList, unselectedList = self._get_lists(selector)
        unselectedList.selectAll()
        self._do_move(unselectedList, selectedList)

    def _deselect_all(self, selector):
        selectedList, unselectedList = self._get_lists(selector)
        selectedList.selectAll()
        self._do_move(selectedList, unselectedList)
        
    def _select(self, selector):
        selectedList, unselectedList = self._get_lists(selector)
        self._do_move(unselectedList, selectedList)

    def _deselect(self, selector):
        selectedList, unselectedList = self._get_lists(selector)
        self._do_move(selectedList, unselectedList)
        
    def _do_move(self, fromList, toList):
        for item in fromList.selectedItems():
            toList.addItem(fromList.takeItem(fromList.row(item)))

    def _get_lists(self, selector):
        """

        :param selector: takes a widget named like agenciesListSelector
        :return: two QListWidgets
        """
        selectorName = selector.objectName()
        stem = selectorName.replace('Selector', '')
        stem = stem[0].capitalize() + stem[1:]

        selectedList = selector.findChild(
            QtGui.QListWidget, 'selected%s' % stem)
        unselectedList = selector.findChild(
            QtGui.QListWidget, 'unselected%s' % stem)

        return selectedList, unselectedList