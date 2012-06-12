.. _modules:

High-Level API modules
==============================================================================
.. currentmodule:: eqcatalogue
.. automodule:: eqcatalogue.homogeniser
.. autoclass:: Homogeniser
.. automethod:: Homogeniser.set_scales

Low-Level API modules
==============================================================================

Filtering
------------------------------------------------------------------------------

.. currentmodule:: eqcatalogue
.. automodule:: eqcatalogue.filtering
.. autoclass:: MeasureFilter
.. automethod:: MeasureFilter.all
.. automethod:: MeasureFilter.count
.. automethod:: MeasureFilter.combine
.. automethod:: MeasureFilter.events
.. automethod:: MeasureFilter.before
.. automethod:: MeasureFilter.after
.. automethod:: MeasureFilter.between
.. automethod:: MeasureFilter.filter
.. automethod:: MeasureFilter.with_agencies
.. automethod:: MeasureFilter.with_magnitude_scales
.. automethod:: MeasureFilter.within_polygon
.. automethod:: MeasureFilter.within_distance_from_point
.. automethod:: MeasureFilter.group_measures

Grouping
------------------------------------------------------------------------------

.. currentmodule:: eqcatalogue
.. automodule:: eqcatalogue.grouping
.. autoclass:: GroupMeasuresByEventSourceKey
.. autoclass:: GroupMeasuresByHierarchicalClustering

Regression
------------------------------------------------------------------------------

.. currentmodule:: eqcatalogue
.. automodule:: eqcatalogue.regression

Selection
------------------------------------------------------------------------------

.. currentmodule:: eqcatalogue
.. automodule:: eqcatalogue.selection
.. autoclass:: MeasureManager
.. automethod:: MeasureManager.append

.. autoclass:: MissingUncertaintyStrategy
.. automethod:: MissingUncertaintyStrategy.should_be_discarded
.. automethod:: MissingUncertaintyStrategy.get_default

.. autoclass:: MUSDiscard
.. autoclass:: MUSSetEventMaximum
.. autoclass:: MUSSetDefault

.. autoclass:: MeasureSelection
.. automethod:: MeasureSelection.select

.. autoclass:: Random
.. autoclass:: Precise
.. autoclass:: AgencyRanking
