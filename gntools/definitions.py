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
The data model uses German names by default, but a user can override these names using a definition table,
which is stored in the geodatabase as GN<solution>_DEFINITION (e.g. GNELE_DEFINITION).

The :class:`DefinitionTable` class reads all key-value pairs from the definition table in the database.
If no match with a certain key has been found, the default German object name is returned.

The default German names and the mappings to their English counterparts
are defined in the :py:mod:`gntools.common.const` module.

The :class:`RelationTable` class reads the intertable-relationships from the GNREL_DEFINITION table in the geodatabase.
"""

import abc as _abc
from collections import namedtuple as _ntuple
from warnings import warn as _warn

from gntools.common import const as _const
from gpf import lookups as _lookups
from gpf import paths as _paths
from gpf.common import validate as _vld
from gpf.common import textutils as _tu
from gpf.tools import queries as _queries


# Namedtuple base class for storing relation definitions
_Relation = _ntuple('Relation', 'target_table relate_table source_field target_field relate_source relate_target type')


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

    **Params:**

    -   **definition** (:class:`DefinitionTable`):

        A DefinitionTable instance.
    """
    def __init__(self, definition):
        super(TableNames, self).__init__(definition, _const.GNTABLES)


class FieldNames(_Definition):
    """
    Provides access to GEONIS field names for the given definition table.

    **Params:**

    -   **definition** (:class:`DefinitionTable`):

        A DefinitionTable instance.
    """
    def __init__(self, definition):
        super(FieldNames, self).__init__(definition, _const.GNFIELDS)


class DefinitionTable(_lookups.ValueLookup):
    """
    Class that exposes the definitions (named objects) within the GEONIS data model.
    Currently, only table and field names can be retrieved.

    **Params:**

    -   **workspace** (gpf.paths.Workspace):

        The Workspace instance for the GEONIS database.

    -   **solution** (str, unicode):

        The name of the solution (e.g. ELE, GAS etc.) for which to read the definitions.
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


class Relation(_Relation):
    """
    Simple dataholder (``namedtuple``) for a GEONIS table relation.
    These type of objects are stored as values in a :class:`RelationTable` lookup dictionary.
    The source table name for the relation is taken from the key in this dictionary.

    **Params**:

    -   **target_table** (str, unicode):

        The name of the target/destination table that stores the foreign key field.

    -   **relate_table** (str, unicode):

        The name of the relation table (if cardinality is n:m).

    -   **source_field** (str, unicode):

        The name of the primary key field in the source/origin table.

    -   **target_field** (str, unicode):

        The name of the foreign key field in the target/destination table.

    -   **relate_source** (str, unicode):

        The name of the source reference field in the relationship table.

    -   **relate_target** (str, unicode):

        The name of the target reference field in the relationship table.

    -   **type** (str, unicode):

        The name of the relationship type.
    """
    __slots__ = ()


class RelationTable(_lookups.Lookup):
    """
    Class that returns the relationship table for the GEONIS data model as a lookup dictionary.

    Each key in the dictionary either represents the name of the source table (default) or the target table,
    depending on the value of the *reverse* argument.

    For each key, a :class:`Relation` is returned with the:

    -   target table (value of source table if *reverse* is ``True``)
    -   relationship table (``None`` if not set)
    -   source key field (target reference field if *reverse* is ``True``)
    -   target reference field (source key field if *reverse* is ``True``)
    -   relationship source reference field (``None`` if not set, target reference field if *reverse* is ``True``)
    -   relationship target reference field (``None`` if not set, source reference field if *reverse* is ``True``)
    -   relation type name

    Note that the relationship table values will only be set if the cardinality of the relationship is *n:m*.

    **Params:**

    -   **workspace** (gpf.paths.Workspace):

        The Workspace instance for the GEONIS database.

    -   **relation_type** (str, unicode):

        An optional name of the relationship type (on which to filter).
        Note that the :py:mod:`gntools.common.const` module contains all the
        relationship type names (constants starting with GNRELTYPE_*).

    -   **reverse** (bool):

        If set to ``True``, the relationship is mapped from target to source. The default is ``False``.

    .. seealso::    :class:`Relation`
    """

    def __init__(self, workspace, relation_type, reverse=False):

        rel_types = (_const.GNRELTYPE_AGGREGRATE, _const.GNRELTYPE_COMPOSITE, _const.GNRELTYPE_DATALINK,
                     _const.GNRELTYPE_ENTITY, _const.GNRELTYPE_LABEL, _const.GNRELTYPE_PLAN,
                     _const.GNRELTYPE_RELATE, _const.GNRELTYPE_SHAPEGROUP)

        # Check if workspace is a Workspace instance and that a valid relation_type has been set
        _vld.pass_if(isinstance(workspace, _paths.Workspace), ValueError,
                     '{!r} requires a {} object'.format(DefinitionTable.__name__, _paths.Workspace.__name__))
        _vld.pass_if(relation_type in rel_types, ValueError,
                     'relation_type must be one of {}'.format(_tu.format_iterable(rel_types, _const.TEXT_OR)))

        # Construct relation definition table path and where clause
        table_path = str(workspace.make_path(_const.GNTABLE_RELATION_DEF))
        type_filter = _queries.Where(_const.GNFIELD_REL_TYPE, '=', relation_type)

        # Set required fields
        src_table = _const.GNFIELD_REL_TABLE_SRC
        dst_table = _const.GNFIELD_REL_TABLE_DST
        src_field = _const.GNFIELD_REL_KEYFIELD_SRC
        dst_field = _const.GNFIELD_REL_KEYFIELD_DST
        src_rel = _const.GNFIELD_REL_RELFIELD_SRC
        dst_rel = _const.GNFIELD_REL_RELFIELD_DST
        if reverse:
            src_table = _const.GNFIELD_REL_TABLE_DST
            dst_table = _const.GNFIELD_REL_TABLE_SRC
            src_field = _const.GNFIELD_REL_KEYFIELD_DST
            dst_field = _const.GNFIELD_REL_KEYFIELD_SRC
            src_rel = _const.GNFIELD_REL_RELFIELD_DST
            dst_rel = _const.GNFIELD_REL_RELFIELD_SRC
        fields = (dst_table, _const.GNFIELD_REL_TABLE_REL, src_field,
                  dst_field, src_rel, dst_rel, _const.GNFIELD_REL_TYPE)

        try:
            # Try and build a relationship lookup
            super(RelationTable, self).__init__(table_path, src_table, fields, type_filter)
        except RuntimeError:
            _warn("Failed to read GEONIS relation table '{}'".format(table_path),
                  DefinitionWarning)

    def _process_row(self, row, **kwargs):
        """ Stores each row in the relationship definition table as ``Relation`` objects. """
        formatted = [(v.upper() if isinstance(v, basestring) else v) for v in row[1:]]
        key, values = formatted[0], Relation(*formatted[1:])
        if not key:
            return
        if key in self:
            _warn("Source table '{}' participates in multiple {} relationships".format(key.upper(), values.type),
                  DefinitionWarning)
            return
        self[key] = values
