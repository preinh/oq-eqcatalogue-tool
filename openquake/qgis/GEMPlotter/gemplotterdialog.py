# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GEMPlotterDialog
                                 A QGIS plugin
 An utility to plot GEM models
                             -------------------
        begin                : 2013-02-26
        copyright            : (C) 2013 by GEM
        email                : michele@openquake.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from ui_gemplotter import Ui_GEMPlotter
from openquake.nrmllib.risk.parsers import \
    FragilityModelParser, VulnerabilityModelParser
try:
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
    from matplotlib.figure import Figure
except ImportError:
    raise ImportError(
        'In order to use the GEMPlotter you need to install '
        'Matplotlib (http://matplotlib.org) and then reload the plugin')


class GEMPlotterDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_GEMPlotter()
        self.ui.setupUi(self)
        self.modelfile = None
        self.ff = {}  # fragility functions dictionary
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(True)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setParent(self)
        self.ui.plotLayout.addWidget(self.canvas)

    @QtCore.pyqtSlot()
    def on_cancelButton_clicked(self):
        self.close()

    @QtCore.pyqtSlot()
    def on_saveButton_clicked(self):
        choices = 'PNG (*.png)|*.png'
        path = unicode(QtGui.QFileDialog.getSaveFileName(
            self, 'Save plot', '', choices))
        self.canvas.print_figure(path)

    @QtCore.pyqtSlot(int)
    def plot_ff(self, taxonomy_idx):
        if taxonomy_idx <= 0:
            return
        self.axes.clear()
        taxonomy = str(self.ui.taxonomyCombo.itemText(taxonomy_idx))
        iml, ys = self.ff[taxonomy]
        for state, y in zip(self.states, ys):
            self.axes.plot(iml['imls'], y, label=state)
        self.axes.legend(loc='upper left')
        self.canvas.draw()
        self.ui.saveButton.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_chooseButton_clicked(self):
        self.modelfile = unicode(QtGui.QFileDialog.getOpenFileName(
            self, 'Select Fragility Model file',
            QtCore.QDir.homePath(),
            'Model files (*.xml)'))
        # TODO: what to do if modelfile is empty?
        # what to do if the file is incorrect?
        self._fillCombo()
        self.ui.taxonomyCombo.currentIndexChanged.connect(self.plot_ff)

    def _fillCombo(self):
        p = iter(FragilityModelParser(self.modelfile))
        kind, self.states = next(p)
        self.ff = dict((taxonomy, (iml, y))
                       for taxonomy, iml, y, no_damage_limit in p)
        self.ui.taxonomyCombo.clear()
        self.ui.taxonomyCombo.addItems(['Taxonomy'] + self.ff.keys())
        self.ui.taxonomyCombo.setEnabled(True)
