import unittest
import os
from datetime import datetime

from tests.test_utils import in_data_dir

from eqcatalogue import models, selection
from eqcatalogue.filtering import EventFilter
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
        homo.set_selector(selection.PrecisionStrategy)
        homo.add_model(LinearModel)
        self._plot_and_assert(homo, 'first')

        homo.reset_filters()
        homo.add_filter(before=datetime.now())
        ranking = {"ML": ["ISC", "IDC"], "mb": ["ISC", "FUNV"]}
        homo.set_selector(selection.AgencyRankingStrategy, ranking=ranking)
        homo.set_scales("ML", "mb")
        homo.add_model(PolynomialModel, order=2)
        self._plot_and_assert(homo, 'second')

        homo.reset_filters()
        homo.add_filter(between=(datetime(2010, 2, 28, 4, 11), datetime.now()),
                        agency__in=["NIED", "IDC"],
                        scale__in=["ML", "mb"])
        homo.set_selector(selection.PrecisionStrategy)
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


class CatalogueTool(unittest.TestCase):

    def test_first_config(self):
        # Apply event selection
        events = EventFilter().with_agencies("ISC", "BJI")

        # Computing Magnitude Scaling Relationship
        emsr = EmpiricalMagnitudeScalingRelationship.make_from_events(
            "mb", "MS", events, selection.PrecisionStrategy)
        emsr.apply_regression_model(LinearModel)

        # Plotting results
        graph_filename = 'first_config.png'
        mpl.plot(emsr, in_data_dir(graph_filename))

        # Assert
        self.assertTrue(os.path.exists(in_data_dir(graph_filename)))

    def test_second_config(self):
        # Apply event selection
        events = EventFilter().before(datetime.now())

        # Computing Magnitude Scaling Relationship
        ranking = {"ML": ["ISC", "IDC"], "mb": ["ISC", "FUNV"]}
        emsr = EmpiricalMagnitudeScalingRelationship.make_from_events(
            "ML", "mb", events, selection.AgencyRankingStrategy(ranking))
        emsr.apply_regression_model(LinearModel)
        emsr.apply_regression_model(PolynomialModel, order=2)

        # Plotting results
        graph_filename = 'second_config.png'
        mpl.plot(emsr, in_data_dir(graph_filename))

        # Assert
        self.assertTrue(os.path.exists(in_data_dir(graph_filename)))

    def test_third_config(self):
        # Apply event Selection
        polygon = 'POLYGON((127.40 30.24, 144.36 49.96, 150.22 34.78))'
        events = EventFilter().\
            between(datetime(2010, 2, 28, 4, 11), datetime.now()).\
            within_polygon(polygon).\
            with_agencies("NIED", "IDC").\
            with_magnitude_scales("ML", "mb")

        # Computing Magnitude Scaling Relationship
        emsr = EmpiricalMagnitudeScalingRelationship.make_from_events("ML",
            "mb", events, selection.PrecisionStrategy,
            missing_uncertainty_strategy=selection.MUSSetEventMaximum())
        emsr.apply_regression_model(LinearModel)

        # Plotting results
        graph_filename = 'third_config.png'
        mpl.plot(emsr, in_data_dir(graph_filename))

        # Assert
        self.assertTrue(os.path.exists(in_data_dir(graph_filename)))

    def test_fourth_config(self):
        # Apply event Selection
        events = EventFilter().\
            between(datetime(2010, 2, 28, 4, 11), datetime.now()).\
            with_agencies("NEIC", "IDC").\
            with_magnitude_scales("ML", "mb")

        # Computing Magnitude Scaling Relationship
        emsr = EmpiricalMagnitudeScalingRelationship.make_from_events("ML",
            "mb", events, selection.PrecisionStrategy,
            missing_uncertainty_strategy=selection.MUSSetDefault(0.2))
        emsr.apply_regression_model(LinearModel)
        emsr.apply_regression_model(PolynomialModel, order=3)

        # Plotting results
        graph_filename = 'fourth_config.png'
        mpl.plot(emsr, in_data_dir(graph_filename))

        # Assert
        self.assertTrue(os.path.exists(in_data_dir(graph_filename)))

    def test_fifth_config(self):
        # Apply event Selection
        point = 'POINT(138.80 33.80)'
        distance = 10000000
        events = EventFilter().\
            within_distance_from_point(point, distance)

        # Computing Magnitude Scaling Relationship
        emsr = EmpiricalMagnitudeScalingRelationship.make_from_events("ML",
            "mb", events, selection.PrecisionStrategy,
            missing_uncertainty_strategy=selection.MUSDiscard())
        emsr.apply_regression_model(LinearModel)

        # Plotting results
        graph_filename = 'fifth_config.png'
        mpl.plot(emsr, in_data_dir(graph_filename))

        # Assert
        self.assertTrue(os.path.exists(in_data_dir(graph_filename)))
