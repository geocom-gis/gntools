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
The *datasource* module simplifies working with GEONIS Datasource XML files.
"""

import os as _os
from xml.etree import cElementTree as _Xml

import gntools.common.const as _const
import gpf.common.textutils as _tu
import gpf.paths as _paths

# GEONIS Datasource XML tags of interest
_GN_XMLTAG_PARAM = 'param'
_GN_XMLTAG_KEY = 'key'
_GN_XMLTAG_VALUE = 'value'
_GN_XMLTAG_TXT = 'text'

# GEONIS Datasource XML keys or element names of interest
_GN_XMLKEY_PATH = 'path'
_GN_XMLKEY_SDEF = 'sdefile'
_GN_XMLKEY_QLFR = 'qualifier'
_GN_XMLKEY_MEDM = 'medium'

# Default GEONIS directory names
_DIRNAME_DATASRC = 'datasources'
_DIRNAME_PROJECT = 'projects'
_DIRNAME_GNMEDIA = 'media'


class Datasource(_paths.Workspace):
    """
    Datasource(datasource)

    Helper class to read a GEONIS Datasource XML, so that the user is able to generate fully qualified paths
    for elements (tables, feature datasets etc.) in an Esri workspace.
    To GEONIS, an Esri Workspace means an SDE connection file or a local File/Personal Geodatabase.

    **Params:**

    -   **xml_path** (str, unicode):

        The full GEONIS Datasource XML file path.

    :raises ValueError: If the GEONIS Datasource XML does not exist or failed to parse.

    .. note::           All class methods are inherited from :class:`gpf.paths.Workspace`.
                        The initialization process of the *Datasource* class is different, because it will read the
                        workspace path from the GEONIS Datasource XML.
                        Another difference is that the *Datasource* class also stores the
                        GEONIS :py:attr:`medium` it applies to. Furthermore, it features 2 helper functions, which
                        try to guess the paths of the media directory (:func:`get_media_dir`)
                        and the project directory (:func:`get_project_dir`) for that same medium.
    """

    def __init__(self, xml_path):
        # Use absolute path to read XML
        xml_abs = _os.path.realpath(xml_path)
        xml_root = self._parse_xml(xml_abs)

        # Try to find GEONIS base path from XML path (often a mapped drive letter, e.g. 'Q:')
        self._gnbase = _paths.find_parent(xml_abs, _DIRNAME_DATASRC)

        # Extract DB parameters and GEONIS medium and initialize Workspace
        db_path, qualifier, self._medium = self._get_props(xml_root)
        db_root = _os.path.dirname(xml_abs) if not _os.path.isabs(db_path) else None
        super(Datasource, self).__init__(db_path, qualifier, db_root)

    @staticmethod
    def _parse_xml(xml_path):
        """ Parses the XML file and returns the root Element. """
        try:
            tree = _Xml.parse(xml_path)
        except (TypeError, OSError, _Xml.ParseError) as e:
            raise ValueError('Failed to parse GEONIS Datasource XML {}: {}'.format(_tu.to_repr(xml_path), e))
        return tree.getroot()

    @staticmethod
    def _get_props(xml_root):
        """ Returns a tuple of (DB path, DB qualifier, medium) from a GEONIS Datasource XML root element. """
        db_path = _const.CHAR_EMPTY
        qualifier = _const.CHAR_EMPTY

        # Get DB parameters
        for param in xml_root.iter(_GN_XMLTAG_PARAM):
            key = param.attrib.get(_GN_XMLTAG_KEY)
            value = param.attrib.get(_GN_XMLTAG_VALUE, _const.CHAR_EMPTY)
            if key in (_GN_XMLKEY_PATH, _GN_XMLKEY_SDEF):
                db_path = _os.path.normpath(value)
            elif key == _GN_XMLKEY_QLFR:
                qualifier = value

        # Read GEONIS medium
        medium = getattr(xml_root.find(_GN_XMLKEY_MEDM), _GN_XMLTAG_TXT, None)

        return db_path, qualifier, medium

    @property
    def medium(self):
        """ Returns the name of the GEONIS medium to which the data source applies. """
        return self._medium

    def get_media_dir(self):
        """
        Gets the derived full path to the corresponding GEONIS media directory.

        :raises OSError:     When the derived directory path does not exist.
        """
        dir_path = _paths.concat(self._gnbase, _DIRNAME_GNMEDIA)
        if not _os.path.isdir(dir_path):
            raise OSError('GEONIS media directory {!r} does not exist'.format(dir_path))
        return dir_path

    def get_project_dir(self):
        """
        Gets the derived full path to the corresponding GEONIS project directory.

        :raises OSError:     When the derived directory path does not exist.
        """
        dir_path = _paths.concat(self._gnbase, _DIRNAME_PROJECT)
        if not _os.path.isdir(dir_path):
            raise OSError('GEONIS project directory {!r} does not exist'.format(dir_path))
        return dir_path
