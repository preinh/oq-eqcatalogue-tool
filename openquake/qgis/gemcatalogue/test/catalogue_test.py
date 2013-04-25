import os
import unittest
import uuid

from openquake.qgis.gemcatalogue.eqcatalogue_qgis.catalogue import EqCatalogue
from openquake.qgis.gemcatalogue.eqcatalogue_qgis.importer_dialog \
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

    def test_IASPEI(self):
        db_name = str(uuid.uuid1())
        self.eqcat.create_db(
            IASPEI, ImporterDialog.IASPEI_PATTERN, db_name)
        self.eqcat.update_catalogue_db(db_name)
        checked_agencies = map(
            str, self.eqcat.dock.agenciesComboBox.checkedItems())
        checked_mscales = map(
            str, self.eqcat.dock.mscalesComboBox.checkedItems())
        self.assertEqual(checked_agencies, ['IASPEI'])
        self.assertEqual(checked_mscales, ['MS', 'mb'])

    def test_ISF(self):
        db_name = str(uuid.uuid1())
        self.eqcat.create_db(
            ISF, ImporterDialog.ISF_PATTERN, db_name)
        self.eqcat.update_catalogue_db(db_name)
        checked_agencies = map(
            str, self.eqcat.dock.agenciesComboBox.checkedItems())
        checked_mscales = map(
            str, self.eqcat.dock.mscalesComboBox.checkedItems())
        self.assertEqual(checked_agencies, ['GUC', 'BKK', 'JMA', 'NIED', 'IGQ', 'KMA', 'MOS', 'NEIC', 'BJI', 'GCMT', 'DJA', 'ISCJB', 'ISC', 'SJA', 'IDC', 'SZGRF', 'MAN'])
        self.assertEqual(checked_mscales, ['ME', 'mbtmp', 'ms1mx', 'Ms', 'mb', 'Ms7', 'ML', 'mB', 'M', 'Mw', 'Ms1', 'MW', 'MLv', 'MS', 'mb1mx', 'Mb', 'MD', 'mb1', 'Muk']
)


if __name__ == '__main__':
    unittest.main()
