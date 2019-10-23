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
The definitions module provides access to object names within the GEONIS data model (e.g. tables, fields etc.).
The data model uses German names originally, but a user can override these names using a definition table,
which is also stored in the geodatabase as GN<solution>_DEFINITION (e.g. GNELE_DEFINITION).

The :class:`DefinitionTable` class reads all key-value pairs from the definition table in the database.
If no match with a certain key has been found, the default German object name is returned.

The default German names and the mappings to their English counterparts
are defined in the :py:mod:`~gntools.common.const` module.
"""

import abc as _abc
from warnings import warn as _warn

from gntools.common import const as _const
from gpf import paths as _paths
from gpf.tools import queries as _queries
from gpf.common import validate as _vld
from gpf import lookups as _lookups


class DefinitionWarning(UserWarning):
    """ This warning is shown when the definitions for a certain solution are not available (yet). """
    pass


class _Definition:
    """ Abstract base class for all definition mappings. """

    __metaclass__ = _abc.ABCMeta
    __slots__ = '_def', '_map'

    @_abc.abstractmethod
    def __init__(self, definition, mapping):
        self._def = definition
        self._map = mapping.get(self._def.solution, {})

    def __getattr__(self, item):
        mapping = self._map.get(item)
        if not mapping:
            # __dir__ already tells the user which attributes are available, but this might not always be clear
            raise AttributeError("{!r} object has no attribute '{}'".format(self.__class__.__name__, item))
        # If the first value in the mapping is not found, return the second value (= default)
        return self._def.get(*mapping)

    def __dir__(self):
        return self._map.keys()


class TableNames(_Definition):
    """
    Provides access to GEONIS table names for the given definition table.

    :param definition:  A DefinitionTable instance.
    :type definition:   DefinitionTable
    """
    def __init__(self, definition):
        super(TableNames, self).__init__(definition, _const.GNTABLES)


class FieldNames(_Definition):
    """
    Provides access to GEONIS field names for the given definition table.

    :param definition:  A DefinitionTable instance.
    :type definition:   DefinitionTable
    """
    def __init__(self, definition):
        super(FieldNames, self).__init__(definition, _const.GNFIELDS)


class DefinitionTable(_lookups.ValueLookup):
    """
    Class that exposes the definitions (named objects) within the GEONIS data model.
    Currently, only table and field names can be retrieved.

    :param workspace:   The Workspace instance for the GEONIS database.
    :param solution:    The name of the solution (e.g. ELE, GAS etc.) for which to read the definitions.
    :type workspace:    gpf.paths.Workspace
    :type solution:     str, unicode
    """

    def __init__(self, workspace, solution):

        # Check if workspace is a Workspace instance
        _vld.pass_if(isinstance(workspace, _paths.Workspace), ValueError,
                     '{!r} requires a {} object'.format(DefinitionTable.__name__, _paths.Workspace.__name__))

        # Construct definition table path for the given solution
        table_path = str(workspace.make_path(_const.GNTABLE_SOLUTION_DEF.format(solution)))

        try:
            # Try and get a lookup for the solution
            super(DefinitionTable, self).__init__(table_path, _const.GNFIELD_NAME, _const.GNFIELD_VALUE)
        except RuntimeError:
            _warn("Failed to read GEONIS definition table for the '{}' solution".format(solution.upper()),
                  DefinitionWarning)
        self.solution = solution.lower()

    @property
    def tablenames(self):
        """
        Provides access to GEONIS table names for the given solution.

        :rtype:     TableNames
        """
        return TableNames(self)

    @property
    def fieldnames(self):
        """
        Provides access to GEONIS field names for the given solution.

        :rtype:     FieldNames
        """
        return FieldNames(self)


class RelationTable(_lookups.RowLookup):
    """
    Class that returns a relationship table for the GEONIS data model.

    :param workspace:       The Workspace instance for the GEONIS database.
    :param relation_type:   The name of the relationship type.
    :param reverse:         If set to ``True``, the relation is mapped from target to source.
                            The default is ``False``.
    :type workspace:        gpf.paths.Workspace
    :type relation_type:    str, unicode
    :type reverse:          bool
    """

    def __init__(self, workspace, relation_type=None, reverse=False):

        # Check if workspace is a Workspace instance and relation_type is set
        _vld.pass_if(isinstance(workspace, _paths.Workspace), ValueError,
                     '{!r} requires a {} object'.format(DefinitionTable.__name__, _paths.Workspace.__name__))

        # Construct relation definition table path and where clause
        table_path = str(workspace.make_path(_const.GNTABLE_RELATION_DEF))
        type_filter = None
        if relation_type:
            type_filter = _queries.Where(_const.GNFIELD_REL_TYPE, '=', relation_type)
        src_table = _const.GNFIELD_REL_TABLE_DST if reverse else _const.GNFIELD_REL_TABLE_SRC
        dst_table = _const.GNFIELD_REL_TABLE_SRC if reverse else _const.GNFIELD_REL_TABLE_DST
        fields = (dst_table, _const.GNFIELD_REL_KEYFIELD_SRC, _const.GNFIELD_REL_KEYFIELD_DST)

        try:
            # Try and get a lookup for the solution
            super(RelationTable, self).__init__(table_path, src_table, fields, type_filter)
        except RuntimeError:
            _warn("Failed to read GEONIS relation table '{}'".format(table_path),
                  DefinitionWarning)
