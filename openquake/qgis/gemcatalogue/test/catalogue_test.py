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
            'Events-2008:2008-5.0:8.0-mb,MS-IASPEI')
        self.assertEqual(feature_count, 0)

        # 61 features with magnitude in the range [1, 8]
        self.eqcat.dock.mag_range.setLowValue(1)
        self.eqcat.dock.mag_range.setHighValue(8)
        feature_count = self._filter_button(
            'Events-2008:2008-1.0:8.0-mb,MS-IASPEI')
        self.assertEqual(feature_count,58)

    def test_ISF(self):
        self._import_data(ISF, ImporterDialog.ISF_PATTERN)
        feature_count = self._filter_button(
            'Events-2010:2010-5.0:8.0-M,mb,mB,Mb,mb1,mb1mx,mbtmp,MD,ME,ML,MLv,'
            'Ms,MS,Ms1,ms1mx,Ms7,Muk,Mw,MW-BJI,BKK,DJA,GCMT,GUC,IDC,IGQ,ISC,'
            'ISCJB,JMA,MAN,MOS,NEIC,NIED,SJA,SZGRF')
        self.assertEqual(feature_count, 173)

    def test_load_countries(self):
        self.eqcat.load_countries()
        layerName = 'Population density'
        layer = QgsMapLayerRegistry.instance().mapLayersByName(
            layerName)[-1]
        self.assertEqual(layerName, str(layer.name()))

    def _filter_button(self, layername):
        btn = self.eqcat.dock.filterBtn
        QtTest.QTest.mouseClick(btn, QtCore.Qt.LeftButton)
        events = QgsMapLayerRegistry.instance().mapLayersByName(
            layername)
        for l in QgsMapLayerRegistry.instance().mapLayers():
            print l
        assert events, 'Could not find layer named %s' % layername
        return events[0].featureCount()

if __name__ == '__main__':
    unittest.main()
