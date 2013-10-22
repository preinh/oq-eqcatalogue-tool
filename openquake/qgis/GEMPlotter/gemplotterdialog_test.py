import os
import sys
import unittest

from gemplotterdialog import GEMPlotterDialog
from PyQt4 import QtGui

FRAGMODEL = os.path.expanduser('~/oq-nrmllib/examples/fragm_d.xml')

app = QtGui.QApplication(sys.argv)


class GEMPlotterTestCase(unittest.TestCase):
    def setUp(self):
        self.dialog = GEMPlotterDialog()
        self.dialog.modelfile = FRAGMODEL
        self.dialog._fillCombo()

    def test_taxonomies(self):
        combo = self.dialog.ui.taxonomyCombo
        items = map(combo.itemText, range(combo.count()))
        self.assertEqual(['Taxonomy', 'RC/DMRF-D/LR', 'RC/DMRF-D/HR'], items)
        self.assertTrue(combo.isEnabled())

    def test_plot(self):
        self.dialog.ui.saveButton.setEnabled(False)
        c = self.dialog.ui.taxonomyCombo
        c.currentIndexChanged.connect(self.dialog.plot_ff)
        try:
            c.setCurrentIndex(c.findText('RC/DMRF-D/LR'))
            self.assertTrue(self.dialog.ui.saveButton.isEnabled())
        finally:
            c.currentIndexChanged.disconnect()

if __name__ == '__main__':
    unittest.main()
