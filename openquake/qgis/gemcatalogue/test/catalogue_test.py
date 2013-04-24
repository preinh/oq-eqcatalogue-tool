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


class CatalogueTestCase(unittest.TestCase):
    def setUp(self):
        self.eqcat = EqCatalogue(IFACE)

    def _import_data(self, catfile, pattern):
        db_name = str(uuid.uuid1())
        db = self.eqcat.create_db(catfile, pattern, db_name)
        try:
            self.eqcat.update_catalogue_db(db_name)
        finally:
            db.close()
            os.remove(db_name)

    def test_IASPEI(self):
        # no features with the default selections
        self._import_data(IASPEI, ImporterDialog.IASPEI_PATTERN)
        feature_count = self._filter_button(
            'Events-1970:2013-5.0:8.0-MS,mb-IASPEI')
        self.assertEqual(feature_count, 0)

        # 61 features with magnitude in the range [1, 8]
        self.eqcat.dock.mag_range.setLowValue(1)
        self.eqcat.dock.mag_range.setHighValue(8)
        feature_count = self._filter_button(
            'Events-1970:2013-1.0:8.0-MS,mb-IASPEI')
        self.assertEqual(feature_count, 61)

    def test_ISF(self):
        self._import_data(ISF, ImporterDialog.ISF_PATTERN)
        feature_count = self._filter_button(
            'Events-1970:2013-5.0:8.0-ME,mbtmp,ms1mx,Ms,mb,Ms7,ML,mB,M,Mw,'
            'Ms1,MW,MLv,MS,mb1mx,Mb,MD,mb1,Muk-GUC,BKK,JMA,NIED,IGQ,KMA,MOS,'
            'NEIC,BJI,GCMT,DJA,ISCJB,ISC,SJA,IDC,SZGRF,MAN')
        self.assertEqual(feature_count, 174)

    def test_load_countries(self):
        self.eqcat.load_countries()
        layer = QgsMapLayerRegistry.instance().mapLayersByName(
            'World Countries')[-1]
        self.assertEqual('World Countries', str(layer.name()))

    def _filter_button(self, layername):
        btn = self.eqcat.dock.filterBtn
        QtTest.QTest.mouseClick(btn, QtCore.Qt.LeftButton)
        events = QgsMapLayerRegistry.instance().mapLayersByName(
            layername)
        assert events, 'Could not find layer named %s' % layername
        return events[0].featureCount()

if __name__ == '__main__':
    unittest.main()
