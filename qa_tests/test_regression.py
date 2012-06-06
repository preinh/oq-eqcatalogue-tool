import unittest

from tests.test_utils import in_data_dir

from eqcatalogue import models, managers, selection
from eqcatalogue.regression import EmpiricalMagnitudeScalingRelationship
from eqcatalogue.importers import isf_bulletin


class AregressionToolShould(unittest.TestCase):

    def setUp(self):
        db = models.CatalogueDatabase(memory=True)
        isf_bulletin.V1.import_events(
            file(in_data_dir('isc-query-small.html')), db)
        events = managers.EventManager().with_agencies("ISC")
        emsr = EmpiricalMagnitudeScalingRelationship.make_from_events(
            "mb", "MS", events, selection.RandomStrategy())


    def test_produce_valid_linear_regression_models(self):
        pass