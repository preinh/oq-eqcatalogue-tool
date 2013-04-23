import os
import unittest
import uuid

from PyQt4 import QtCore, QtTest
from qgis.core import QgsMapLayerRegistry

from openquake.qgis.gemcatalogue.catalogue import EqCatalogue
from openquake.qgis.gemcatalogue.importer_dialog \
    import ImporterDialog
from openquake.qgis.gemcatalogue.test.app import getTestApp

QGISAPP, CANVAS, IFACE, PARENT = getTestApp()

basedir = __file__
for i in range(5):
    basedir = os.path.dirname(os.path.abspath(basedir))

datadir = os.path.join(basedir, 'tests', 'data')
## $HOME/oq-eqcatalogue-tool/tests/data

ISF = os.path.join(datadir, 'isc-query-small.html')
IASPEI = os.path.join(datadir, 'iaspei.csv')


def layerdict():
    layers = QgsMapLayerRegistry.instance().mapLayers().values()
    return dict((str(l.name()), l) for l in layers)


class CatalogueTestCase(unittest.TestCase):
    def setUp(self):
        self.eqcat = EqCatalogue(IFACE)

    def _check(self, catfile, pattern, expected_agencies, expected_mscales):
        db_name = str(uuid.uuid1())
        self.eqcat.create_db(
            catfile, pattern, db_name)
        self.eqcat.update_catalogue_db(db_name)
        checked_agencies = map(
            str, self.eqcat.dock.agenciesComboBox.checkedItems())
        checked_mscales = map(
            str, self.eqcat.dock.mscalesComboBox.checkedItems())
        self.assertEqual(checked_agencies, expected_agencies)
        self.assertEqual(checked_mscales, expected_mscales)
        self._filter_button()
        os.remove(db_name)

    def test_IASPEI(self):
        self._check(IASPEI, ImporterDialog.IASPEI_PATTERN,
                    ['IASPEI'], ['MS', 'mb'])

    def test_ISF(self):
        self._check(ISF, ImporterDialog.ISF_PATTERN, [
            'GUC', 'BKK', 'JMA', 'NIED', 'IGQ', 'KMA', 'MOS', 'NEIC',
            'BJI', 'GCMT', 'DJA', 'ISCJB', 'ISC', 'SJA', 'IDC', 'SZGRF',
            'MAN'],
            ['ME', 'mbtmp', 'ms1mx', 'Ms', 'mb', 'Ms7', 'ML', 'mB', 'M', 'Mw',
             'Ms1', 'MW', 'MLv', 'MS', 'mb1mx', 'Mb', 'MD', 'mb1', 'Muk']
        )

    def test_load_countries(self):
        self.eqcat.load_countries()
        layers = layerdict()
        self.assertIn('World Countries', layers)

    def _filter_button(self):
        btn = self.eqcat.dock.filterBtn
        QtTest.QTest.mouseClick(btn, QtCore.Qt.LeftButton)
        events = layerdict()['Events']
        self.assertEqual(events.featureCount(), 0)

if __name__ == '__main__':
    unittest.main()
