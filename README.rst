Welcome to GEONIS Tools
=======================

|python| |status| |pypi| |build| |issues| |docs|

.. |python| image:: https://img.shields.io/pypi/pyversions/gntools?logo=python
    :alt: Python version(s)

.. |status| image:: https://img.shields.io/pypi/status/gntools
    :alt: PyPI status

.. |pypi| image:: https://img.shields.io/pypi/v/gntools?logo=pypi
    :alt: PyPI homepage
    :target: https://pypi.org/project/gntools

.. |build| image:: https://img.shields.io/appveyor/ci/geonis-github/gntools?logo=appveyor
    :alt: AppVeyor
    :target: https://ci.appveyor.com/project/GEONIS-GITHUB/gntools

.. |issues| image:: https://img.shields.io/github/issues-raw/geocom-gis/gntools?logo=github
    :alt: GitHub issues
    :target: https://github.com/geocom-gis/gntools/issues

.. |docs| image:: https://img.shields.io/readthedocs/gntools?logo=read%20the%20docs
    :alt: Documentation
    :target: https://gntools.readthedocs.io/en/latest/

Purpose
-------

The *GEONIS Tools for Geocom Python Framework* package (``gntools``) consists of a set of Python modules that contain tools, helpers, loggers etc. that simplify the development of menu or form scripts for GEONIS_.

Please note that the ``gntools`` package has been developed for **Python 2.7.14+ (ArcGIS Desktop/Server) ONLY**.

.. _GEONIS: https://geonis.com/en/solutions/framework/geonis

Requirements
------------

- ArcGIS Desktop and/or ArcGIS Server 10.6 or higher
- Python 2.7.14 or higher (along with the ``arcpy`` module)
- Geocom Python Framework (the ``gpf`` package on GitHub_ or PyPI_)

.. _GitHub: https://github.com/geocom-gis/gpf
.. _PyPI: https://pypi.org/project/gpf

Installation
------------

The easiest way to install the GEONIS Tools, is to use pip_, a Python package manager.
When ``pip`` is installed, the user can simply run:

    ``python -m pip install gntools``

Notice that ``pip`` will also install the ``gpf`` dependency, if it's missing.

.. _pip: https://pip.pypa.io/en/stable/installing/

Documentation
-------------

The complete ``gntools`` documentation can be found at `Read the Docs`_.

.. _Read the Docs: https://gntools.readthedocs.io/

License
-------

`Apache License 2.0`_ © 2019 Geocom Informatik AG / VertiGIS & contributors

.. _Apache License 2.0: https://github.com/geocom-gis/gntools/blob/master/LICENSE
