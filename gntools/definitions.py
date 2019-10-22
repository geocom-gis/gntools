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

from gntools.common import const
from gpf.lookups import ValueLookup as _ValueLookup


class _Definition:
    """ Abstract base class for all definition mappings. """

    __metaclass__ = _abc.ABCMeta
    __slots__ = '_def', '_map'

    @_abc.abstractmethod
    def __init__(self, definition):
        self._map = {}
        self._def = definition

    def __getattr__(self, item):
        solution = self._map.get(self._def.solution)
        if not solution:
            # The mappings for the given solution are not available: they need to be defined in gntools.common.const
            raise NotImplementedError("Mappings for the '{}' solution have not been defined".format(self._def.solution))
        mapping = solution.get(item)
        if not mapping:
            # This should not happen often, since __dir__ already tells the user which attributes are available
            raise AttributeError("{!r} object has no attribute '{}'".format(self.__class__.__name__, item))
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
        super(TableNames, self).__init__(definition)
        self._map = const.GNTABLES


class FieldNames(_Definition):
    """
    Provides access to GEONIS field names for the given definition table.

    :param definition:  A DefinitionTable instance.
    :type definition:   DefinitionTable
    """
    def __init__(self, definition):
        super(FieldNames, self).__init__(definition)
        self._map = const.GNFIELDS


class DefinitionTable(_ValueLookup):
    """
    Class that exposes the definitions (named objects) within the GEONIS data model.
    Currently, only table and field names can be retrieved.

    :param workspace:   The Workspace instance for the GEONIS database.
    :param solution:    The name of the solution (e.g. ELE, GAS etc.) for which to read the definitions.
    :type workspace:    gpf.paths.Workspace
    :type solution:     str, unicode
    """

    def __init__(self, workspace, solution):
        table_path = str(workspace.make_path(const.GNTABLE_SOLUTION_DEF.format(solution)))
        super(DefinitionTable, self).__init__(table_path, const.GNFIELD_NAME, const.GNFIELD_VALUE)
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
