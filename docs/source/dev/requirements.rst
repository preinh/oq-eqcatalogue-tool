.. _requirements:

Software dependencies
==============================================================================

This part of documentation covers the installation of Earthquake event
catalogue homogeniser tool. Earthquake event catalogue homogeniser
tool `Python 2.7.x`_ version of the interpreter and `Spatialite
3.0.x`_. The first step is getting external dependencies properly
installed. Earthquake event catalogue homogeniser tool requires these
libraries in order to be used:

* GeoAlchemy_ >= 0.7.x
* SqlAlchemy_ >= 0.7.x
* Scipy_ >= 0.10.x 
* Numpy_ >= 1.6.x
* Matplotlib_ >= 1.1.x
* PIL_ >= 1.0.x

Instructions for setting up GeoAlchemy with Spatialite are provided here_.

Get the code
=============================================================================

Earthquake event catalogue homogeniser tool is actively developed on
GitHub, where the code is `available
<https://github.com/gem/oq-eqcatalogue-tool>`_. You can clone the
repository doing::

    git clone git@github.com:gem/oq-eqcatalogue-tool.git

Or download the
`zip <https://github.com/gem/oq-eqcatalogue-tool/zipball/master>`_.


.. Links
.. _Python 2.7.x: http://www.python.org/getit/releases/2.7/
.. _Spatialite 3.0.x: http://www.gaia-gis.it/gaia-sins/
.. _GeoAlchemy: http://www.geoalchemy.org
.. _SqlAlchemy: http://www.sqlalchemy.org/
.. _Scipy: http://www.scipy.org/
.. _Numpy: http://numpy.org/
.. _Matplotlib: http://matplotlib.sourceforge.net/
.. _PIL: http://www.pythonware.com/products/pil/
.. _here: http://www.geoalchemy.org/usagenotes.html#notes-for-spatialite


Install dependencies with PIP
=============================================================================
You can install all the dependencies (except for pysqlite2) by issuing:

    pip install -r requirements.txt

Where `requirements.txt` points to the file in the main source directory.

Pysqlite2 installation requires manual installation as described here_.
