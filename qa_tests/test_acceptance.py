import unittest
import numpy as np
import os
from datetime import datetime

from tests.test_utils import in_data_dir

from eqcatalogue import models, selection
from eqcatalogue.managers import EventManager
from eqcatalogue.regression import (EmpiricalMagnitudeScalingRelationship,
                                    LinearModel, PolynomialModel)
from eqcatalogue.serializers import mpl


DB = models.CatalogueDatabase(filename=in_data_dir('qa.db'))


class CatalogueTool(unittest.TestCase):

    def test_first_config(self):
        # Apply event selection
        events = EventManager().with_agencies("ISC", "BJI")

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
        events = EventManager().with_agencies("ISC").before(datetime.now())

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
        events = EventManager().\
            between(datetime(2010, 2, 28, 4, 11), datetime.now()).\
            within_polygon(polygon).\
            with_agencies("NIED", "IDC").\
            with_magnitudes("ML", "mb")

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
        events = EventManager().\
            between(datetime(2010, 2, 28, 4, 11), datetime.now()).\
            with_agencies("NEIC", "IDC").\
            with_magnitudes("ML", "mb")

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
        events = EventManager().\
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
