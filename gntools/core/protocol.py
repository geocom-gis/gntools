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
This module can be used to write text and features to the GEONIS Protocol (XML).
The Protocol is typically used to report issues (e.g. validation) with certain features.
"""

import os as _os
from calendar import timegm as _timegm
from datetime import datetime as _dt
from datetime import timedelta as _td
from time import mktime as _mktime
# noinspection PyPep8Naming
from xml.etree import cElementTree as _xml

import gpf.common.guids as _guids
import gpf.common.textutils as _tu
import gpf.common.validate as _vld
import gpf.tools.workspace as _ws
import gntools.common.geometry as _geometry

_GNLOG_ENCODING = 'iso-8859-1'

_GNLOG_TYPE_HEADER1 = 0
_GNLOG_TYPE_HEADER2 = 1
_GNLOG_TYPE_MESSAGE = 2  # In Delphi code, this is called GNLogMsg
_GNLOG_TYPE_WARNING = 3
_GNLOG_TYPE_FAILURE = 4
_GNLOG_TYPE_NOTICE = 5  # In Delphi code, this is called GnLogInfo

_ESRI_FIELD_SHAPE = 'Shape'
_ESRI_FIELD_GLOBALID = 'GlobalID'

_ATTR_CONN = 'con'
_ATTR_TABLE = 'tbl'
_ATTR_FIELD = 'fld'
_ATTR_VALUE = 'val'
_ATTR_PRJROOT = 'projectroot'
_ATTR_PRJNAME = 'currentproject'
_ATTR_MSG = 'message'
_ATTR_MSGTYPE = 'messagetype'
_ATTR_DATE = 'date'
_ATTR_LASTMOD = 'lastchangedate'
_ATTR_READONLY = 'isreadonly'

_TAG_ROOT = 'ObjectLog'
_TAG_ENTRY = 'Entry'
_TAG_OBJECT = 'Object'
_TAG_CFUNC = 'CustomFunctions'
_TAG_FEATURE = 'feature'
_TAG_DATAID = 'dataid'

# Define constants for get_delphi_time() function
_DELPHI_EPOCH = _timegm(_dt(1899, 12, 30).timetuple())
_TZ_OFFSET = _mktime(_dt.now().utctimetuple()) - _mktime(_dt.utcnow().utctimetuple())
_DAY_SECONDS = _td(days=1).total_seconds()

# Object caches for memoization of calculated values
_time_cache = {}
_table_cache = {}


def get_delphi_time(time=None):
    """
    Gets the current time (optionally, for a given time) expressed as a formatted floating point string for Delphi.

    :param time:    A datetime object. When not set, :func:`now` is used.
    :return:        A string-formatted floating point value, specifying the number of days since 1899/12/30.
    :rtype:         str
    """
    global _time_cache

    if not time:
        # get current local time if `time` was not specified
        time = _dt.now()
    elif not isinstance(time, _dt):
        raise TypeError("'time' should be a datetime object or None")

    time_key = repr(time)

    try:
        # look if this time has already been calculated and return it
        delphi_time = _time_cache[time_key]
    except KeyError:
        # time_key not found: convert datetime object to timestamp float
        time = _mktime(time.timetuple())

        # add Delphi epoch offset + UTC time offset (no DST) to timestamp and divide by seconds per day
        delphi_time = '{:.13f}'.format((abs(_DELPHI_EPOCH) + _TZ_OFFSET + time) / _DAY_SECONDS)
        _time_cache[time_key] = delphi_time

    return delphi_time


class ProtocolFeature(object):
    """
    ProtocolFeature(table, global_id, {geometry}, {globalid_field})

    Creates a ProtocolFeature for GEONIS Protocol logging purposes.

    :param table:               The full path to the table or feature class that contains the logged feature.
    :param global_id:           GlobalID value of the logged feature.
    :param geometry:            Esri `Geometry` instance or EsriJSON string.
    :keyword globalid_field:    If the *GlobalID* field has a different name, specify it using this option.
    :type table:                str, unicode
    :type global_id:            str, unicode, gpf.tools.guids.Guid
    :type geometry:             str, Geometry
    :type globalid_field:       str, unicode
    """

    __slots__ = ('_table', '_guid', '_shape', '_gidfld')

    def __init__(self, table, global_id, geometry=None, **kwargs):
        self._table = table
        self._guid = _guids.Guid(global_id)
        self._shape = geometry
        self._gidfld = kwargs.get('globalid_field', _ESRI_FIELD_GLOBALID)

    def _get_workspace(self):
        """ Extracts a tuple of (root workspace, unqualified table name) from *table_path*. """
        global _table_cache

        table = _os.path.basename(self._table)
        try:
            workspace = _table_cache[table]
        except KeyError:
            workspace = _ws.WorkspaceManager.get_root(self._table)
        return workspace, table.split(_tu.DOT)[-1]

    def _get_dataid_attrs(self):
        """ Returns a dictionary of attributes that can be used to populate the <dataid> XML element. """
        db_path, tb_name = self._get_workspace()
        return {
            _ATTR_CONN:  db_path,
            _ATTR_TABLE: tb_name,
            _ATTR_FIELD: self._gidfld,
            _ATTR_VALUE: self.fid
        }

    def _add_geometry(self, parent_element):
        """ Appends a <geometry> XML element for the current record to `parent_element`. """
        if not self._shape:
            return

        xml_geom = _geometry.serialize(self._shape)
        parent_element.append(xml_geom)

    @property
    def fid(self):
        """
        Returns the (validated) GlobalID of the current ProtocolFeature feature.

        :rtype: str
        """
        return str(self._guid)

    def write_elements(self, parent_element):
        """
        Adds a <feature> XML element to the *parent_element* based on the current ProtocolFeature values.

        :param parent_element:  Element
        """
        feature = _xml.SubElement(parent_element, _TAG_FEATURE)
        _xml.SubElement(feature, _TAG_DATAID, self._get_dataid_attrs())
        self._add_geometry(parent_element)


class ProtocolLogger(object):
    """
    ProtocolLogger({project_path}, {output_path}, {encoding})

    Logger class to write GEONIS XML protocols (e.g. for validations etc.).

    The *project_path* argument must be set on the first ``ProtocolLogger`` call.
    Since ProtocolLogger is a singleton, instantiating it multiple times will always return the same object
    if the class is initialized without arguments (*project_path* = ``None``).
    """

    __slots__ = '_root', '_prj_path', '_prj_name'
    __instance = None

    def __new__(cls, project_path=None):

        if cls.__instance is not None and project_path is None:
            return cls.__instance

        _vld.pass_if(project_path, TypeError,
                     '{!r} must be instantiated with a `project_path` argument'.format(cls.__name__))

        ProtocolLogger.__instance = object.__new__(cls)
        ProtocolLogger.__instance._prj_path, ProtocolLogger.__instance._prj_name = cls._get_project(project_path)
        ProtocolLogger.__instance._set_root()
        return ProtocolLogger.__instance

    @staticmethod
    def _get_attrs(msg, msg_type):
        """
        Populates an Entry attribute dictionary and returns it.
        All Entries receive a date attribute, which is a Delphi-compatible floating point value.

        :param msg:         The message to set. When not specified, the attribute will be omitted (used for blank line).
        :param msg_type:    The message type (warning, error, etc.)
        :return:            An keyword argument dictionary
        """
        entry_attrs = {
            _ATTR_MSGTYPE:  str(msg_type),
            _ATTR_DATE:     get_delphi_time(),
            _ATTR_LASTMOD:  str(0),
            _ATTR_READONLY: str(False).lower()  # TODO??
        }
        if msg not in (_tu.EMPTY_STR, None):
            entry_attrs[_ATTR_MSG] = msg
        return entry_attrs

    @staticmethod
    def _get_project(project_path):
        """ Returns a ``tuple`` of (project directory, project name) for the specified *project_path*. """
        if not project_path:
            return None, None
        project_dir, project_name = _os.path.split(project_path)
        # By adding an empty string, we ensure that a slash is added at the end of the path
        return _os.path.join(_os.path.realpath(project_dir.strip()), _tu.EMPTY_STR), project_name

    def _set_root(self):
        """ Creates and sets the root element for the GEONIS XML Protocol file. """
        root = _xml.Element(_TAG_ROOT)
        root.set(_ATTR_PRJROOT, self._prj_path)
        root.set(_ATTR_PRJNAME, self._prj_name)
        self._root = root

    def _add_entry(self, msg, msg_type, gn_feature=None, function=None):
        """
        Adds an <Entry> node to the GEONIS XML root node.

        :param msg:         The message to set. When not specified, the attribute will be omitted (used for blank line).
        :param msg_type:    The message type (warning, error, etc.).
        :param gn_feature:  An optional feature to log in the <Object> node.
        :param function:    An optional custom function to log in the <CustomFunctions> node. Not supported yet.
        """
        entry = _xml.SubElement(self._root, _TAG_ENTRY, self._get_attrs(msg, msg_type))
        self._add_object(entry, gn_feature)
        self._add_function(entry, function)

    @staticmethod
    def _add_object(parent, gn_feature):
        """
        Adds an <Object> node to the specified parent (Entry) node.

        :param parent:      The XML Element to which the SubElement should be added.
        :param gn_feature:  A feature to add to the <Object> node. May be ``None``.
        """
        obj = _xml.SubElement(parent, _TAG_OBJECT)
        if not gn_feature:
            return
        gn_feature.write_elements(obj)

    @staticmethod
    def _add_function(parent, function=None):
        """
        Adds a <CustomFunctions> node to the specified parent (<Entry>) node.

        :param parent:      The XML Element to which the SubElement should be added.
        :param function:    A function to add to the <CustomFunctions> node. Not supported yet.
        """
        _xml.SubElement(parent, _TAG_CFUNC)
        _vld.raise_if(function, NotImplementedError, 'Custom functions are not supported yet')

    def _write_tree(self, output_path, encoding=_GNLOG_ENCODING):
        """ Indents the current root element and its children, wraps it into an ElementTree and writes an XML. """

        def indent(element, level=0, last_child=False):
            spacing = _tu.LF + level * _tu.TAB
            num_children = len(element)
            if num_children:
                if _vld.has_value(element.text, True):
                    element.text = spacing + _tu.TAB
                for i, child in enumerate(element, 1):
                    indent(child, level + 1, i == num_children)
            if _vld.has_value(element.tail, True):
                element.tail = spacing[:-1] if last_child else spacing

        indent(self._root)
        tree = _xml.ElementTree(self._root)
        tree.write(output_path, encoding=encoding, xml_declaration=True)
        del tree

    def message(self, message, gn_feature=None):
        """
        Logs a basic message to the GEONIS XML protocol, optionally accompanied by a feature.

        :param message:     Text message to log.
        :param gn_feature:  Feature object to add to the log entry.
        :type message:      str, unicode
        :type gn_feature:   gntools.core.protocol.ProtocolFeature
        """
        self._add_entry(message, _GNLOG_TYPE_MESSAGE, gn_feature)

    def info(self, message, gn_feature=None):
        """
        Logs an info notice to the GEONIS XML protocol, optionally accompanied by a feature.

        :param message:     Text message to log.
        :param gn_feature:  Feature object to add to the log entry.
        :type message:      str, unicode
        :type gn_feature:   gntools.core.protocol.ProtocolFeature
        """
        self._add_entry(message, _GNLOG_TYPE_NOTICE, gn_feature)

    def warn(self, message, gn_feature=None):
        """
        Logs a warning to the GEONIS XML protocol, optionally accompanied by a feature.

        :param message:     Text message to log.
        :param gn_feature:  Feature object to add to the log entry.
        :type message:      str, unicode
        :type gn_feature:   gntools.core.protocol.ProtocolFeature
        """
        self._add_entry(message, _GNLOG_TYPE_WARNING, gn_feature)

    def error(self, message, gn_feature=None):
        """
        Logs an error to the GEONIS XML protocol, optionally accompanied by a feature.

        :param message:     Text message to log.
        :param gn_feature:  Feature object to add to the log entry.
        :type message:      str, unicode
        :type gn_feature:   gntools.core.protocol.ProtocolFeature
        """
        self._add_entry(message, _GNLOG_TYPE_FAILURE, gn_feature)

    def blank(self):
        """ Logs a blank Entry to the GEONIS XML protocol (appears as a blank line in the protocol window). """
        self._add_entry(_tu.EMPTY_STR, _GNLOG_TYPE_MESSAGE)

    def header(self, message, gn_feature=None):
        """
        Logs a header to the GEONIS XML protocol, optionally accompanied by a feature.

        :param message:     Text message to log.
        :param gn_feature:  Feature object to add to the log entry.
        :type message:      str, unicode
        :type gn_feature:   gntools.core.protocol.ProtocolFeature
        """
        self._add_entry(message, _GNLOG_TYPE_HEADER1, gn_feature)

    def subheader(self, message, gn_feature=None):
        """
        Logs a subheader to the GEONIS XML protocol, optionally accompanied by a feature.

        :param message:     Text message to log.
        :param gn_feature:  Feature object to add to the log entry.
        :type message:      str, unicode
        :type gn_feature:   gntools.core.protocol.ProtocolFeature
        """
        self._add_entry(message, _GNLOG_TYPE_HEADER2, gn_feature)

    def flush(self, output_path, encoding=None):
        """
        Flushes the XML element buffer and writes the GEONIS Protocol to a file.

        Once this function is called, you can reuse the ProtocolLogger for the same project.
        If you want to start logging for a another project, re-initialize the ProtocolLogger with a new project path.

        :param output_path:     The full path to the output protocol XML that should be written.
        :keyword encoding:      Optional encoding to use for the protocol file (default = ISO-8859-1).
        :type output_path:      str, unicode
        :type encoding:         str, unicode

        .. warning::            The user must have write access in the specified output directory.
        """
        xml_path = _os.path.realpath(output_path.strip())
        dirname, filename = _os.path.split(xml_path)
        if not _os.path.isdir(dirname):
            _os.makedirs(dirname)

        self._write_tree(output_path, encoding)
        self._set_root()
