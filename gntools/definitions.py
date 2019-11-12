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

The default German names and the mappings to their English counterparts are defined in the classes in this module.

The :class:`RelationTable` class reads the inter-table-relationships from the GNREL_DEFINITION table in the geodatabase.
"""

from warnings import warn as _warn

from gntools.common import const as _const
from gntools.common import i18n as _i18n
from gpf import lookups as _lookups
from gpf import paths as _paths
from gpf.common import validate as _vld
from gpf.common import textutils as _tu
from gpf.tools import queries as _queries

# Store the current GEONIS language globally, once it has been determined
_gn_lang = None

# The following key needs to exist in the definitions table.
# If it exists and the value does not match the one given below, it is assumed that GEONIS uses the default definitions.
_EN_KEY = 'tablename_sec_cable_dense'
_EN_VAL = 'eles_spannung'

# Definition key prefixes (for filtering purposes).
_KEY_PREFIX_TABLES = 'tablename'
_KEY_PREFIX_FIELDS = 'fieldname'


class DefinitionTable(_lookups.ValueLookup):
    """
    Class that exposes the definitions (named objects) within the GEONIS data model.

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

        # Construct definition table path for the given workspace and solution
        table_path = str(workspace.make_path(_const.GNTABLE_SOLUTION_DEF.format(solution)))

        try:
            # Try and get a lookup for the solution
            super(DefinitionTable, self).__init__(table_path, _const.GNFIELD_NAME, _const.GNFIELD_VALUE)
        except RuntimeError:
            raise RuntimeError("Failed to read GEONIS definition table for the '{}' solution".format(solution.upper()))

        if not self:
            # The table is empty: this should never happen under normal circumstances
            raise ValueError('There are no definitions for the {} solution'.format(solution.upper()))

        self._solution = solution.lower()

    @property
    def solution(self):
        """ Returns the (lowercase) solution name to which this definitions table applies. """
        return self._solution


class _Definition(object):
    """ Base class for all definition mappings. """
    __slots__ = '_def', '_prefix', '_override'

    def __init__(self, definitions, filter_prefix):
        _vld.pass_if(isinstance(definitions, DefinitionTable), ValueError,
                     "'definitions' argument must be a DefinitionTable instance")
        self._def = definitions
        self._prefix = filter_prefix

        # This feels a bit hacky, but it's actually similar to how it is determined in the GEONIS core code...
        self._override = self._def.get(_EN_KEY, _EN_VAL) != _EN_VAL

    def _get_name(self, key_template, default_template):
        """
        Finds a specific key in the definition table.
        Returns a default when not found or when there are no overrides.
        """
        default = default_template.format(self._def.solution)
        if not self._override:
            return default.lower()
        return self._def.get(key_template.format(self._prefix), default).lower()

    def _get_default(self, template_en, template_de):
        """
        Returns an english name when self._override is True or a german name otherwise.
        The templates will be prepended with the solution name.
        """
        if self._override:
            return template_en.format(self._def.solution).lower()
        return template_de.format(self._def.solution).lower()


class _EleTableNames(_Definition):
    """
    Provides access to GEONIS table names for the electric solution.

    **Params:**

    -   **definitions** (:class:`DefinitionTable`):

        A DefinitionTable instance. The table must fit the electric solution.
    """

    strand = property(lambda self: self._get_name('{}_branch', '{}_strang'))
    cable = property(lambda self: self._get_name('{}_cable', '{}_kabel'))
    construction_line = property(lambda self: self._get_name('{}_construction_line', '{}_bauobjekt_lin'))
    cs_base = property(lambda self: self._get_name('{}_cs_base', '{}_qs_basis'))
    cs_cable = property(lambda self: self._get_name('{}_cs_cable', '{}_qs_kabel'))
    cs_area = property(lambda self: self._get_name('{}_cs_frame', '{}_qs_fla'))
    cs_pipe = property(lambda self: self._get_name('{}_cs_pipe', '{}_qs_rohr'))
    cs_pipe_pipe = property(lambda self: self._get_name('{}_cs_pipepipe', '{}_qs_rohr_rohr'))
    cs_cable_protect_pos = property(lambda self: self._get_name('{}_cs_posnum_label', '{}t_qs_kabelschutzpos'))
    dd_connector = property(lambda self: self._get_name('{}_ds_connector', '{}_ds_verbinder'))
    dd_cable_connector = property(lambda self: self._get_name('{}_ds_cableconnector', '{}_ds_kabelverbindung'))
    dd_clamp = property(lambda self: self._get_name('{}_clamp', '{}_ds_klemme'))
    dd_transition = property(lambda self: self._get_name('{}_ds_inout', '{}_ds_uebergang'))
    dd_station = property(lambda self: self._get_name('{}_ds_station', '{}_ds_station'))
    dd_transformer = property(lambda self: self._get_name('{}_ds_transformer', '{}_ds_transformer'))
    house = property(lambda self: self._get_name('{}_house_conn', '{}_hausanschluss'))
    lighting = property(lambda self: self._get_name('{}_luminary', '{}_leuchte'))
    pipe = property(lambda self: self._get_name('{}_pipe', '{}_rohr'))
    rel_cable_route = property(lambda self: self._get_name('{}_route_cable', '{}r_trasse_kabel'))
    rel_pipe_cable = property(lambda self: self._get_name('{}_pipe_cable', '{}r_rohr_kabel'))
    rel_pipe_pipe = property(lambda self: self._get_name('{}_pipe_pipe', '{}r_rohr_rohr'))
    rel_route_rohr = property(lambda self: self._get_name('{}_route_pipe', '{}r_route_pipe'))
    route = property(lambda self: self._get_name('{}_route', '{}_trasse'))
    sec_cable_voltage = property(lambda self: self._get_name('{}_sec_cable_dense', '{}s_spannung'))
    sec_cable_protect = property(lambda self: self._get_name('{}_sec_cable_protect', '{}s_kabelschutz_rohr'))
    sec_cs_cable = property(lambda self: self._get_name('{}_sec_cable_cs', '{}s_querschnitt_kabel'))
    sec_cs_route = property(lambda self: self._get_name('{}_typ_querschnitt', '{}s_querschnitt_trasse'))
    sec_cs_scaling = property(lambda self: self._get_name('{}_querschnitt_skalierung',
                                                          '{}s_querschnitt_skalierung'))
    sec_net_color = property(lambda self: self._get_name('{}_sec_netcolor', '{}s_netzfarbe'))
    sec_type_dd = property(lambda self: self._get_name('{}_typ_ds', '{}s_typ_ds'))
    sec_type_route = property(lambda self: self._get_name('{}_typ_trasse', '{}s_typ_trasse'))
    sleeve = property(lambda self: self._get_name('{}_sleeve_socket', '{}_muffe'))
    small_connection = property(lambda self: self._get_name('{}_small_conn', '{}_kleinanschluss'))
    t_cs_cable = property(lambda self: self._get_name('{}_t_cs_cable', '{}t_qs_kabel'))
    t_cs_rohr = property(lambda self: self._get_name('{}_t_cs_pipe', '{}t_qs_rohr'))
    t_cs_rohr_rohr = property(lambda self: self._get_name('{}_t_cs_pipe_pipe', '{}t_qs_rohr_rohr'))


class _EleFieldNames(_Definition):
    """
    Provides access to GEONIS field names for the electric solution.

    **Params:**

    -   **definition** (:class:`DefinitionTable`):

        A DefinitionTable instance. The table must fit the electric solution.
    """

    # Looked up properties
    cable_protect = property(lambda self: self._get_name('{}_cable_protect', 'kabelschutz'))
    cable_ref = property(lambda self: self._get_name('{}_cable_ref', 'kabel_ref'))
    clamp_number = property(lambda self: self._get_name('{}_clamp_number', 'nummer'))
    code_ref = property(lambda self: self._get_name('{}_code_ref', 'code'))
    cs_angle = property(lambda self: self._get_name('{}_cs_angle', 'symbolori'))
    cs_mapscale = property(lambda self: self._get_name('{}_cs_mapscale', 'mapscale'))
    cs_ref = property(lambda self: self._get_name('{}_cs_ref', 'qs_ref'))
    cs_released = property(lambda self: self._get_name('{}_cs_released', 'released'))
    cs_type = property(lambda self: self._get_name('{}_cs_typ', 'querschnitt'))
    cs_visible = property(lambda self: self._get_name('{}_cs_visible', 'visible'))
    cs_width = property(lambda self: self._get_name('{}_cs_width', 'breite'))
    dd_ref = property(lambda self: self._get_name('{}_ds_ref', 'ds_ref'))
    ddhv_ref = property(lambda self: self._get_name('{}_dshs_ref', 'dshs_ref'))
    ddlv_ref = property(lambda self: self._get_name('{}_dsns_ref', 'dsns_ref'))
    ddmv_ref = property(lambda self: self._get_name('{}_dsms_ref', 'dsms_ref'))
    ddpl_ref = property(lambda self: self._get_name('{}_dsob_ref', 'dsob_ref'))
    info_text = property(lambda self: self._get_name('{}_elementinfo', 'infotext'))
    feature_link = property(lambda self: self._get_name('{}_featurelink', 'featurelink'))
    index = property(lambda self: self._get_name('{}_idx', 'idx'))
    ipipe_ref = property(lambda self: self._get_name('{}_ipipe_ref', 'inner_rohr_ref'))
    length = property(lambda self: self._get_name('{}_length', 'laenge'))
    opipe_ref = property(lambda self: self._get_name('{}_opipe_ref', 'ueber_rohr_ref'))
    pipe_ref = property(lambda self: self._get_name('{}_pipe_ref', 'rohr_ref'))
    position = property(lambda self: self._get_name('{}_posnum', 'posnum'))
    route_index = property(lambda self: self._get_name('{}_trench_idx', 'trasse_idx'))
    route_pos = property(lambda self: self._get_name('{}_trench_pos', 'trasse_pos'))
    route_ref = property(lambda self: self._get_name('{}_route_ref', 'trasse_ref'))
    route_reverse = property(lambda self: self._get_name('{}_trench_reverse', 'reverse'))
    route_type = property(lambda self: self._get_name('{}_trasse_typ', 'typ'))
    station_ref = property(lambda self: self._get_name('{}_station_ref', 'station_ref'))
    strand_ref = property(lambda self: self._get_name('{}_strang_ref', 'strang_ref'))
    text_ori = property(lambda self: self._get_name('{}_text_angle', 'textori'))
    transformer_number = property(lambda self: self._get_name('{}_ds_trafo_name_number', 'name_nummer'))
    transformer_power = property(lambda self: self._get_name('{}_trafo_power', 'leistung'))
    transformer_ref = property(lambda self: self._get_name('{}_trafo_ref', 'trafo_ref'))
    voltage = property(lambda self: self._get_name('{}_dense', 'spannung'))

    # Default properties
    name_number = property(lambda self: self._get_default('name_number', 'name_nummer'))

    @property
    def description(self):
        """ Determines the current GEONIS language and returns the matching description field name for it. """
        global _gn_lang

        # Only read the language once and store it on the global module level
        _gn_lang = _gn_lang or _i18n.get_language()

        return {
            _i18n.GN_LANG_CUSTOM: _const.GNFIELD_DESC_CUSTOM,
            _i18n.GN_LANG_DE:     _const.GNFIELD_DESC_DE,
            _i18n.GN_LANG_EN:     _const.GNFIELD_DESC_EN,
            _i18n.GN_LANG_FR:     _const.GNFIELD_DESC_FR,
            _i18n.GN_LANG_IT:     _const.GNFIELD_DESC_IT
        }.get(_gn_lang, _const.GNFIELD_DESC_DE)


class EleDefinitions(DefinitionTable):

    def __init__(self, workspace, solution=_const.GNMEDIA_ELECTRIC):
        super(EleDefinitions, self).__init__(workspace, solution)

    @property
    def tables(self):
        """ Provides access to GEONIS table names for the ELE solution. """
        return _EleTableNames(self, _KEY_PREFIX_TABLES)

    @property
    def fields(self):
        """ Provides access to GEONIS field names for the ELE solution. """
        return _EleFieldNames(self, _KEY_PREFIX_FIELDS)


class Relation(tuple):
    """
    Simple dataholder (similar to a ``namedtuple``) for a GEONIS table relation.
    These type of objects are stored as values in a :class:`RelationTable` lookup dictionary.
    The source table name for the relation is taken from the key in this dictionary.

    The initialization argument names are equal to the listed property names below.
    """
    __slots__ = ()

    def __new__(cls, target_table=None, relate_table=None, source_field=None, target_field=None,
                relate_source=None, relate_target=None, relate_type=None):
        args = cls._fix_args(target_table, relate_table, source_field, target_field,
                             relate_source, relate_target, relate_type)
        return tuple.__new__(Relation, args)

    @classmethod
    def _fix_args(cls, *args):
        for i in xrange(cls.__new__.func_code.co_argcount - 1):
            try:
                yield args[i]
            except IndexError:
                yield None

    def __nonzero__(self):
        # If all values in the tuple are None, return False.
        return any(self)

    #: The name of the target/destination table that stores the foreign key field.
    target_table = property(lambda self: self[0])

    #: The name of the relation table (if cardinality is n:m).
    relate_table = property(lambda self: self[1])

    #: The name of the primary key field in the source/origin table.
    source_field = property(lambda self: self[2])

    #: The name of the foreign key field in the target/destination table.
    target_field = property(lambda self: self[3])

    #: The name of the source reference field in the relationship table (if cardinality is n:m).
    relate_source = property(lambda self: self[4])

    #: The name of the target reference field in the relationship table (if cardinality is n:m).
    relate_target = property(lambda self: self[5])

    #: The relationship type or cardinality (e.g. "1:n", "1:1", "n:m", "1:0").
    relate_type = property(lambda self: self[6])


class RelationWarning(UserWarning):
    """ Warning that is shown when a bad relation has been detected in the GEONIS relationship table. """
    pass


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
        type_filter = _queries.Where(_const.GNFIELD_REL_TYPE).Equals(relation_type)

        # Define required field default names
        src_table = _const.GNFIELD_REL_TABLE_SRC
        dst_table = _const.GNFIELD_REL_TABLE_DST
        src_field = _const.GNFIELD_REL_KEYFIELD_SRC
        dst_field = _const.GNFIELD_REL_KEYFIELD_DST
        src_rel = _const.GNFIELD_REL_RELFIELD_SRC
        dst_rel = _const.GNFIELD_REL_RELFIELD_DST

        # Switch source and destination fields if 'reverse' is True
        if reverse:
            src_table = _const.GNFIELD_REL_TABLE_DST
            dst_table = _const.GNFIELD_REL_TABLE_SRC
            src_field = _const.GNFIELD_REL_KEYFIELD_DST
            dst_field = _const.GNFIELD_REL_KEYFIELD_SRC
            src_rel = _const.GNFIELD_REL_RELFIELD_DST
            dst_rel = _const.GNFIELD_REL_RELFIELD_SRC

        # Set fields to collect
        fields = (dst_table, _const.GNFIELD_REL_TABLE_REL, src_field,
                  dst_field, src_rel, dst_rel, _const.GNFIELD_REL_TYPE)

        try:
            # Try and build a relationship lookup
            super(RelationTable, self).__init__(table_path, src_table, fields, type_filter)
        except RuntimeError as e:
            raise RuntimeError("Failed to read GEONIS relation table '{}': {}".format(table_path, e))

    def _process_row(self, row, **kwargs):
        """ Stores each row in the relationship definition table as ``Relation`` objects. """
        formatted = [(v.upper().strip() if isinstance(v, basestring) else v) for v in row]
        key, values = formatted[0], Relation(*formatted[1:])
        if not key:
            return
        if key in self:
            _warn("Source table '{}' participates in multiple {} relationships".format(key.upper(), values.relate_type),
                  RelationWarning)
            return
        self[key] = values
