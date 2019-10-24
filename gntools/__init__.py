# coding: utf-8
#
# Copyright 2019 Geocom Informatik AG / VertiGIS

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This is the documentation for the **gntools** package for **Python 2.7** (only).
The package provides a toolset for the creation of GEONIS menu or form scripts.

GEONIS is a powerful GIS solution by Geocom Informatik AG (Switzerland), built on top of ArcGIS technology.
Although this package does not require a license to run and works fully independent of the GEONIS software,
please note that GEONIS itself *does* require a license.

This package is released under the Apache License 2.0 as an open-source product,
allowing the community to freely use it, improve it and possibly add new features.

Several functions in this package require Esri's ``arcpy`` Python library, which does not make this a *free* package.
However, users who have already installed and authorized ArcGIS Desktop (ArcMap, ArcCatalog etc.) should be able to work
with this package without any problems.

One of the most notable classes is the :class:`gntools.protocol.Logger` class,
which can be used to write messages and features to a GEONIS XML log file (or *Protocol*).
Users can read this file back in with GEONIS and click on the listed features,
which is useful for inspection and/or validation purposes.

Also of interest might be the :py:mod:`gntools.params` module. This module contains classes that
help parse passed-in arguments from GEONIS menu or form scripts in a standardized and user-friendly manner.
"""