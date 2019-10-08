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
from xml.etree import cElementTree as _ETree

import gpf.common.textutils as _tu
import gpf.tools.workspace as _ws

_GN_XMLTAG_PARAM = 'param'
_GN_XMLTAG_KEY = 'key'
_GN_XMLTAG_VALUE = 'value'

_GN_XMLKEY_PATH = 'path'
_GN_XMLKEY_SDEF = 'sdefile'
_GN_XMLKEY_QLFR = 'qualifier'


class Datasource(_ws.WorkspaceManager):
    """
    Datasource(datasource)

    Helper class to read a GEONIS Datasource XML, so that the user is able to generate fully qualified paths
    for elements (tables, feature datasets etc.) in an Esri workspace.
    To GEONIS, an Esri Workspace means an SDE connection file or a local File/Personal Geodatabase.

    :param datasource:  The full GEONIS Datasource XML file path.
    :type datasource:   str, unicode
    :raises ValueError: If the GEONIS Datasource XML does not exist or failed to parse.

    .. note::           All methods listed below are inherited from :class:`gpf.tools.workspace.WorkspaceManager`.
                        Only the initialization process of the *Datasource* is different.
                        Generally speaking, users will find the :func:`find_path` and :func:`construct` functions
                        most useful.
    """

    def __init__(self, datasource):
        db_dir, db_file, qualifier = self._read_params(datasource)
        super(Datasource, self).__init__(db_file, qualifier, db_dir)

    @staticmethod
    def _parse_xml(xml_path):
        """ Parses the XML file and returns the root Element. """
        try:
            tree = _ETree.parse(xml_path)
        except (TypeError, OSError, _ETree.ParseError) as e:
            raise ValueError('Failed to parse GEONIS Datasource XML {}: {}'.format(_tu.to_repr(xml_path), e))
        return tree.getroot()

    def _read_params(self, xml_path):
        """ Returns a tuple of (DB dir/root, DB path, DB qualifier) from a GEONIS Datasource XML. """
        db_dir = _tu.EMPTY_STR
        db_path = _tu.EMPTY_STR
        qualifier = _tu.EMPTY_STR

        xml_path = _os.path.realpath(xml_path)
        xml_root = self._parse_xml(xml_path)
        for param in xml_root.iter(_GN_XMLTAG_PARAM):
            key = param.attrib.get(_GN_XMLTAG_KEY)
            value = param.attrib.get(_GN_XMLTAG_VALUE, _tu.EMPTY_STR)
            if key in (_GN_XMLKEY_PATH, _GN_XMLKEY_SDEF):
                db_path = _os.path.normpath(value)
                if not _os.path.isabs(db_path):
                    db_dir = _os.path.dirname(xml_path)
            elif key == _GN_XMLKEY_QLFR:
                qualifier = value
        return db_dir, db_path, qualifier
