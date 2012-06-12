.. _modules:

High-Level API modules
==============================================================================

The High-Level API provides the tools to perform the following tasks:

1. create and access a database with the earthquake events;
2. import event data into a the database;
3. perform the homogenisation of different magnitude scale values and plot the results.

Task 1, 2, 3 are handled by :mod:`~eqcatalogue.models`,
:mod:`~eqcatalogue.importers.isf_bulletin` and
:mod:`~eqcatalogue.homogeniser`, respectively.

Module :mod:`eqcatalogue.homogeniser`
------------------------------------------------------------------------------

.. automodule:: eqcatalogue.homogeniser
.. autoclass:: Homogeniser()
.. automethod:: Homogeniser.__init__([native_scale[, target_scale[, measure_filter[, grouper[, selector[, missing_uncertainty_strategy]]]]]])
.. automethod:: Homogeniser.set_scales

.. automethod:: Homogeniser.add_filter
.. autoattribute:: Homogeniser.AVAILABLE_FILTERS
.. automethod:: Homogeniser.reset_filters
.. automethod:: Homogeniser.events
.. automethod:: Homogeniser.measures

.. automethod:: Homogeniser.set_grouper
.. automethod:: Homogeniser.grouped_measures

.. automethod:: Homogeniser.set_selector
.. automethod:: Homogeniser.set_missing_uncertainty_strategy
.. automethod:: Homogeniser.selected_native_measures
.. automethod:: Homogeniser.selected_target_measures

.. automethod:: Homogeniser.add_model
.. automethod:: Homogeniser.reset_models

.. automethod:: Homogeniser.serialize(filename)
.. automethod:: Homogeniser.plot(filename)

Module :mod:`eqcatalogue.models`
------------------------------------------------------------------------------

.. automodule:: eqcatalogue.models
.. autoclass:: eqcatalogue.models.EventSource
.. autoclass:: eqcatalogue.models.Agency
.. autoclass:: eqcatalogue.models.Event
.. autoclass:: eqcatalogue.models.MagnitudeMeasure
.. autoclass:: eqcatalogue.models.Origin
.. autoclass:: eqcatalogue.models.MeasureMetadata
.. autoclass:: eqcatalogue.models.CatalogueDatabase
.. automethod:: eqcatalogue.models.CatalogueDatabase.recreate
.. automethod:: eqcatalogue.models.CatalogueDatabase.reset_singleton
.. automethod:: eqcatalogue.models.CatalogueDatabase.position_from_latlng
.. automethod:: eqcatalogue.models.CatalogueDatabase.get_or_create

Module :mod:`eqcatalogue.importers.isf_bulletin`
------------------------------------------------------------------------------

.. automodule:: eqcatalogue.importers.isf_bulletin
.. autoclass:: eqcatalogue.importers.isf_bulletin.V1
.. automethod:: eqcatalogue.importers.isf_bulletin.V1.load
.. automethod:: eqcatalogue.importers.isf_bulletin.V1.import_events

Low-Level API modules
==============================================================================
