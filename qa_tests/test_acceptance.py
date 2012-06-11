import unittest
import os
from datetime import datetime

from tests.test_utils import in_data_dir

from eqcatalogue import models, selection
from eqcatalogue.filtering import MeasureFilter
from eqcatalogue.regression import (EmpiricalMagnitudeScalingRelationship,
                                    LinearModel, PolynomialModel)
from eqcatalogue.serializers import mpl
from eqcatalogue.homogeniser import Homogeniser

DB = models.CatalogueDatabase(filename=in_data_dir('qa.db'))


class HomogeniserAPI(unittest.TestCase):

    def _plot_and_assert(self, homo, filename_prefix):
        graph_filename = in_data_dir("qa_homo_%s.png" % filename_prefix)
        homo.plot(graph_filename)
        self.assertTrue(os.path.exists(in_data_dir(graph_filename)))

    def test_different_configs(self):
        homo = Homogeniser("mb", "MS")
        homo.add_filter(agency__in=["ISC", "BJI"])
        homo.set_selector(selection.Precise)
        homo.add_model(LinearModel)
        self._plot_and_assert(homo, 'first')

        homo.reset_filters()
        homo.add_filter(before=datetime.now())
        ranking = {"ML": ["ISC", "IDC"], "mb": ["ISC", "FUNV"]}
        homo.set_selector(selection.AgencyRanking, ranking=ranking)
        homo.set_scales("ML", "mb")
        homo.add_model(PolynomialModel, order=2)
        self._plot_and_assert(homo, 'second')

        homo.reset_filters()
        homo.add_filter(between=(datetime(2010, 2, 28, 4, 11), datetime.now()),
                        agency__in=["NIED", "IDC"],
                        scale__in=["ML", "mb"])
        homo.set_selector(selection.Precise)
        homo.set_missing_uncertainty_strategy(selection.MUSSetDefault,
                                              default=0.2)
        homo.reset_models()
        homo.add_model(LinearModel)
        homo.add_model(PolynomialModel, order=3)
        self._plot_and_assert(homo, 'fourth')

        polygon = 'POLYGON((127.40 30.24, 144.36 49.96, 150.22 34.78))'
        homo.add_filter(within_polygon=polygon)
        homo.set_missing_uncertainty_strategy(selection.MUSSetEventMaximum)
        self._plot_and_assert(homo, 'third')

        point = 'POINT(138.80 33.80)'
        distance = 10000000
        homo.reset_filters()
        homo.add_filter(within_distance_from_point=[point, distance])
        homo.set_missing_uncertainty_strategy(selection.MUSDiscard)
        self._plot_and_assert(homo, 'fifth')

