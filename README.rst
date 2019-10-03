Welcome to GEONIS Tools
=======================

|docs|

.. |docs| image:: https://readthedocs.org/projects/gntools/badge/
    :alt: Documentation Status
    :scale: 100%
    :target: https://gntools.readthedocs.io/en/latest/

Purpose
-------

The *GEONIS Tools for Geocom Python Framework* package (`gntools`) consists of a set of Python modules that contain tools, helpers, loggers etc. that simplify the development of menu or form scripts for GEONIS_.

Please note that the `gntools` package has been developed for **Python 2.7.14+ (ArcGIS Desktop/Server) ONLY**.

.. _GEONIS: https://geonis.com/en/solutions/framework/geonis

Requirements
------------

- ArcGIS Desktop and/or ArcGIS Server 10.6 or higher
- Python 2.7.14 or higher (along with the `arcpy` module)
- Geocom Python Framework (`gpf`_ package)

.. _gpf: https://pypi.org/project/gpf

Installation
------------

The easiest way to install the GEONIS Tools, is to use `pip`_, a Python package manager.
When `pip` is installed, the user can simply run:

    ``python -m pip install gntools``

Notice that `pip` will also install the `gpf` dependency, if it's missing.

.. _pip: https://pip.pypa.io/en/stable/installing/

Documentation
-------------

The complete `gntools` documentation can be found at `Read the Docs`_.

.. _Read the Docs: https://gntools.readthedocs.io/

License
-------

`Apache License 2.0`_ © 2019 Geocom Informatik AG / VertiGIS & contributors

.. _Apache License 2.0: https://github.com/geocom-gis/gntools/blob/master/LICENSE
