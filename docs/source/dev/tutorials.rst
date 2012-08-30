.. _tutorials:

Tutorials
===============================================================================

oq-eqcatalogue-tool - A Basic Primer
=====================================

This quick tutorial aims to get you started using the basic functionalities
of the oq-eqcatalogue-tool, starting with an input catalogue and finishing
with a simple regression plot to compare two different magnitude scales.

Installation
-------------------------------------
The following installation instructions apply to Ubuntu 12.04.

You may need some development packages that you can install with apt:

    sudo apt-get install git mercurial python-software-properties python-imaging python-numpy python-scipy python-matplotlib python-nose libspatialite-dev

Get the code from github:

    git clone http://github.com/gem/oq-eqcatalogue-tool/

Then, install the remaining requirements

    sudo pip install -r oq-eqcatalogue-tool/requirements.txt


To check that the installation works properly you can issue the command
    cd oq-eqcatalogue-tool
    ./run_qa_tests


Data format
-------------------------------------

The input earthquake catalogue comes from a standard query of the 'International
Seismological Centre Bulletin' returned in the classic IASPEI Standard Format (ISF).

An example of an earthquake in this format is given below::

    Event 14342462 Near coast of central Chile
    Date       Time        Err   RMS Latitude Longitude  Smaj  Smin  Az Depth   Err Ndef Nsta Gap  mdist  Mdist Qual   Author      OrigID
    2010/02/28 00:00:43.12   0.49 0.770 -36.6671  -73.4847  16.6  10.6  86   0.0f        43      116   4.66 168.84     uk IDC       16660453
    2010/02/28 00:00:47.30        2.120 -35.8400  -73.6100                  35.0         38       48 155.40 178.50     uk BJI       14395373
    2010/02/28 00:00:47.42   0.27 1.057 -36.6246  -73.3679 9.480 7.417  84  27.0f       852  845  36   4.66 177.69 m i se ISC       00198763
    (#PRIME)

    Magnitude  Err Nsta Author      OrigID
    ML     4.4 0.2    4 IDC       16660453
    MS     4.8 0.2    7 IDC       16660453
    mb     5.0 0.1   22 IDC       16660453
    Ms     5.6       12 BJI       14395373
    mB     5.3       20 BJI       14395373
    MS     5.2 0.1   81 ISC       00198763
    mb     5.3 0.2  162 ISC       00198763

When performing the query is is necessary to ensure that the output weblinks option is unchecked.

Getting Started
--------------------------------------

In the current format the oq-eqcatalogue tool is designed as a python library, 
so the following tutorial utilises the ipython interface. 

Creating and Reading a Database
--------------------------------------

To create a database in which to store the earthquake catalogue we make use of the high
level API module ''Models definition''. In this example the catalogue will be stored in
the database file ''ISC_example_database1.db''::

    from eqcatalogue.models import CatalogueDatabase
    Catalogue = CatalogueDatabase(filename = ''\path\to\ISC_example_database1.db'')

Two additional options, corresponding to spatialite commands, can be set here:

* ''memory'' - If set to ''True'' will load the database into memory. This is faster but will 
require more RAM, so may be appropriate for smaller catalogues
* ''drop'' - Will clear and recreate the database schema (if loading an existing database)

Parsing a Catalogue to a Database
--------------------------------------

To parse the earthquake catalogue (''ISC_example_catalogue.txt'')into the database, the ''Importer'' module is used::
    
    from eqcatalog.importers import isf_bulletin
    isf_bulletin.V1.import_events(file('/path/to/ISC_example_catalogue.txt'), Catalogue)

Depending on the size of the catalogue this step may take anything from a few seconds to a few minutes.


Building the Regression Part 1: Defining the Catalogue Filters
--------------------------------------------------------------


The catalogue homogenisation process applies a series of filters to the catalogue. This is to
refine the data set for regression subject to user-defined restrictions. 

In this example, the following describes the process to select from the catalogue those events
recorded by the ISC agency, containing an "mb" and an "Ms" magnitude value::

    from eqcatalogue.homogenisor import Homogenisor
    hom = Homogenisor(''mb'',''Ms'')

Where ''mb'' (body-wave magnitude) is designated as the *native* magnitude (the independent variable)
and ''Ms'' as the  *target* magnitude (the dependent variable).

Grouping the Events
^^^^^^^^^^^^^^^^^^^

The first step in the homogenisation process is to group the measures so that those measures
representing the same event are identified. Here we group only according to the event key, which
is the key defined in the first row of each event in the IASPEI Standard Format definition of an 
earthquake::
    
    from eqcatalogue.grouping import GroupMeasuresByEventSourceKey
    hom.set_grouper(GroupeMeasuresByEventSourceKey)
    

Adding Filters
^^^^^^^^^^^^^^

The next step is to limit the data to only those events for which the magnitudes from the ''ISC'' 
agency are given::

    hom.add_filter(agency__in = ['ISC'])
    
The catalogue can be refined by applying other different filters (e.g. by time, by location etc.).
The full list of available filters can be found by::

    hom.AVAILABLE_FILTERS
    
    ['agency__in',
     'magnitude__gt',
     'scale__in',
     'between',
     'within_polygon',
     'after',
     'within_distance_from_point',
     'before']
     
Where the inputs are defined as follows:

* ''agency_in'': For the agency filtering, the filters must be specified as a list ''['Agency_Code_1', 'Agency_Code_2', ...]''
* ''magnitude_gt'': Magnitudes greater than ''float'' (e.g. 4)
* ''scale__in'': List of magnitude scales
* ''before'': Before date (as datetime object)
* ''after'': After date (as datetime object)
* ''between'': Between lower and upper dates [lower, upper] (datetime objects)
* ''within_polygon'': Only events with origin inside polygon (polygon specified in well-known text format)
* ''within_distance_from_point: Only events within a distance (km) from the point (specified in well-known text)

If at any point it is necessary to reset the filters, this can be done with the command:

    hom.reset_filters()
   

Selecting a Measure from a Potential Set of Measures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Depending on the filtering strategy applied to the catalogue, it may be common to encounter
circumstances in which, for a single event, multiple measures are retained after filtering 
(i.e. multiple measures may satisfy the database query). At present there are several ways 
this can be treated:

1. Accept all measures in the regression - effectively treating all measures as independent
2. Select a measure at ''Random'' from the possible set for each event 
3. Select the most ''Precise'' measure (i.e. the one with the lowest valid uncertainty)
4. Select from the measure set in order of preference according to agency (''AgencyRanking'')

To implement the strategy the user needs to import the corresponding ''Random'', ''Precise''
or ''AgencyRanking'' class (the accept all option is the default if no selection strategy is 
specified)::

    from eqcatalogue.selection import Random
    hom.set_selector(Random)
    
Choosing a Strategy to Handle Missing Uncertainty Values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The regression tools apply orthogonal distance regression. Therefore, for each measure a corresponding
uncertainty value must be given. As the uncertainty on magnitude is not always reported routinely
for every measure, the user must choose an appropriate strategy to indicate how to define a magnitude
uncertainty.


    from eqcatalogue.selection import MUSSetDefualt
    hom.set_missing_uncertainty_strategy(MUSSetDefault, default=0.3)
    

Current options include:

1. ''MUSDiscard'' - Always discard the measures with missing uncertainties
2. ''MUSSetEventMaximum'' - Take the maximum uncertainty defined by all corresponding measures (discard if none found)
3. ''MUSSetDefault'' - Retain measure and assign a default uncertainty value.

Selecting the Model for Regression
----------------------------------

At present, two model types are currently supported

1. Linear (''LinearModel'')
2. n\ :sup:'th'\ order Polynomial (''PolynomialModel'')

These models are defined in the regression by::

    from eqcatalogue.regression import LinearModel, PolynomialModel
    hom.add_model(LinearModel)
    hom.add_model(PolynomialModel, order=3)

If it is necessary to change or delete the selection of model, this can be done with
the command::
    
    hom.reset_models()

Applying the Regression
------------------------

Once the previous steps have been defined the regression can be implemented. The following
command will apply the orthogonal distance regression, and plot the output in a file called
''/path/to/example_output_file.png''::

    model_output = Homogenisor.serialize('/path/to/example_output_file.png')

In the ''/path/to'' directory an example regression plot ''example_output_file.png'' has been 
produced. To access the other results of the regression, we create a variable called
''model_output''. This is a dictionary with two keys: 

1. ''model'' returns the model class used for the regression
2. ''output'' returns the 'scipy.odr.output <http://docs.scipy.org/doc/scipy/reference/generated/scipy.odr.Output.html#scipy.odr.Output>' class describing the regression output.




.. Links
.. _http://www.isc.ac.uk/iscbulletin/search/bulletin/
