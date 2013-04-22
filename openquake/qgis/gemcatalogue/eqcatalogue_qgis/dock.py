# -*- coding: utf-8 -*-

"""
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from ui_dock import Ui_Dock
from gemcatalogue import log_msg
from collections import namedtuple
from MapTools import PolygonDrawer

Range = namedtuple('Range', 'low_value high_value')


class GemDock(QDockWidget, Ui_Dock):
    def __init__(self, iface, parent=None, gemcatalogue=None):
        QDockWidget.__init__(self, parent)
        self.iface = iface
        self.gemcatalogue = gemcatalogue
        self.setupUi(self)
        self.add_range_sliders()
        self._prevMapTool = None
        self.canvas = self.iface.mapCanvas()

        # Spatial filtering wdg.
        self.polygonDrawer = PolygonDrawer(self.canvas,
                                           {'color': QColor("#666666"),
                                            'enableSnap': False,
                                            'keepAfterEnd': True})
        self.polygonDrawer.setAction(self.drawBtn)
        self.connect(self.polygonDrawer, SIGNAL("geometryEmitted"),
                     self.polygonCreated)
        self.connect(self.drawBtn, SIGNAL("clicked()"), self.drawPolygon)
        self.connect(self.clearBtn, SIGNAL("clicked()"), self.clearPolygon)

    def closeEvent(self, event):
        self.emit(SIGNAL("closed"), self)
        return QDockWidget.closeEvent(self, event)

    def add_range_sliders(self):
        self.mag_range.setOrientation(Qt.Horizontal)
        self.mag_range.setMinimum(1)
        self.mag_range.setMaximum(10)
        self.mag_range.setLowValue(5)
        self.mag_range.setHighValue(8)

        self.date_range.setOrientation(Qt.Horizontal)
        self.date_range.setMinimum(QDate(1970, 01, 01))
        self.date_range.setMaximum(QDate.currentDate())
        self.date_range.setLowValue(QDate(1970, 01, 01))
        self.date_range.setHighValue(QDate.currentDate())

    @pyqtSlot()
    def on_filterBtn_clicked(self):
        selectedItems = self.agenciesCombo.checkedItems()

    def update_selectDbComboBox(self, db_sel):
        if db_sel is not None and db_sel != '':
            if self.selectDbComboBox.count() == 0:
                self.selectDbComboBox.addItem(db_sel)
                self.gemcatalogue.load_data()
            else:
                item_index = self.selectDbComboBox.findText(db_sel)
                self.selectDbComboBox.blockSignals(True)
                # Elem not in list.
                if item_index != -1:
                    self.selectDbComboBox.removeItem(item_index)

                self.selectDbComboBox.insertItem(0, db_sel)
                self.selectDbComboBox.blockSignals(False)
                self.selectDbComboBox.setCurrentIndex(0)

    @pyqtSlot()
    def on_addDbBtn_clicked(self):
        db_sel = unicode(QFileDialog.getOpenFileName(
            self.iface.mainWindow(), 'Choose db',
            QDir.homePath(), "Catalogue db file (*.db);;All files (*.*)"))
        self.update_selectDbComboBox(db_sel)

    @pyqtSlot()
    def on_filterBtn_clicked(self):
        agencies_selected = self.agenciesComboBox.checkedItems()
        mscales_selected = self.mscalesComboBox.checkedItems()
        mvalues_selected = Range(self.mag_range.lowValue(),
                                 self.mag_range.highValue())
        dvalues_selected = ((self.date_range.lowValue()).toPyDateTime(),
                            (self.date_range.highValue()).toPyDateTime())

        self.gemcatalogue.update_map(agencies_selected, mscales_selected,
                                     mvalues_selected, dvalues_selected)

    @pyqtSlot(str)
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

    def storePrevMapTool(self):
        prevMapTool = self.canvas.mapTool()
        if prevMapTool not in (self.polygonDrawer,):
            self._prevMapTool = prevMapTool

    def restorePrevMapTool(self):
        self.polygonDrawer.stopCapture()
        if self._prevMapTool:
            self.canvas.setMapTool(self._prevMapTool)

    def showRubberBands(self, show=True):
        """ show/hide all the rubberbands """
        if self.polygonDrawer.isEmittingPoints:
            self.polygonDrawer.reset()
        else:
            if show:
                self.polygonDrawer.rubberBand.show()
            else:
                self.polygonDrawer.rubberBand.hide()

    def showEvent(self, event):
        self.showRubberBands(True)
        QWidget.showEvent(self, event)

    def hideEvent(self, event):
        self.showRubberBands(False)
        self.restorePrevMapTool()
        QWidget.hideEvent(self, event)

    def drawPolygon(self):
        # store the previous maptool
        self.storePrevMapTool()

        # set the polygon drawer as current maptool
        self.polygonDrawer.startCapture()

    def clearPolygon(self):
        # remove the displayed polygon
        self.polygonDrawer.reset()

    def polygonCreated(self, polygon):
    # restore the previous maptool
        self.restorePrevMapTool()
        log_msg(polygon.exportToWkt())

    def deleteLater(self, *args):
    #print "deleting", self
        self.clearPolygon()

        # restore the previous maptool
        self.restorePrevMapTool()

        # delete the polygon drawer maptool
        self.polygonDrawer.deleteLater()
        self.polygonDrawer = None

        QWidget.deleteLater(self, *args)

    def showRubberBands(self, show=True):
        """ show/hide all the rubberbands """
        if self.polygonDrawer.isEmittingPoints:
            self.polygonDrawer.reset()
        else:
            if show:
                self.polygonDrawer.rubberBand.show()
            else:
                self.polygonDrawer.rubberBand.hide()
