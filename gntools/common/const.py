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
Module with specific GEONIS-related constants.
All GPF constants are imported as well, which means that this module basically extends the gpf.common.const module.
"""

# noinspection PyUnresolvedReferences
from gpf.common.const import *

# GEONIS system tables (templates)
GNTABLE_VERSION = 'gn_version'
GNTABLE_LOOKUP = 'gn_lookup'
GNTABLE_SOLUTION_DEF = 'gn{}_definition'
GNTABLE_RELATION_DEF = 'gnrel_definition'
GNTABLE_RELATION_RULE = 'gnrel_rule'
GNTABLE_RELATION_FORMULA = 'gnrel_formula'
GNTABLE_SPLITMERGE = 'gn_splitmerge_def'

# GEONIS system table fields
GNFIELD_NAME = 'name'
GNFIELD_VALUE = 'value_'

# Default GEONIS media/solution (feature dataset) names
GNMEDIA_STANDARD = 'std'
GNMEDIA_GENERAL = 'div'
GNMEDIA_ELECTRIC = 'ele'
GNMEDIA_WATER = 'was'
GNMEDIA_GAS = 'gas'
GNMEDIA_SEWER = 'sew'
GNMEDIA_HEATING = 'fwa'
GNMEDIA_CADASTRE = 'av'

#: GEONIS table name mappings (English - German) for each solution.
#: Currently, the mappings are only available for the electric solution (ELE) and are not exhaustive.
GNTABLES = {
    GNMEDIA_ELECTRIC: {
        'branch':           ('tablename_branch', 'ele_strang'),
        'cable':            ('tablename_cable', 'ele_kabel'),
        'cable_connection': ('tablename_ds_cableconnector', 'ele_ds_kabelverbindung'),
        'clamp':            ('tablename_clamp', 'ele_ds_klemme'),
        'connector':        ('tablename_ds_connector', 'ele_ds_verbinder'),
        'house':            ('tablename_house_conn', 'ele_hausanschluss'),
        'lighting':         ('tablename_luminary', 'ele_leuchte'),
        'pipe':             ('tablename_pipe', 'ele_rohr'),
        'rel_cable_route':  ('tablename_route_cable', 'eler_trasse_kabel'),
        'rel_pipe_cable':   ('tablename_pipe_cable', 'eler_rohr_kabel'),
        'rel_pipe_pipe':    ('tablename_pipe_pipe', 'eler_rohr_rohr'),
        'rel_route_rohr':   ('tablename_route_pipe', 'eler_route_pipe'),
        'route':            ('tablename_route', 'ele_trasse'),
        'sleeve':           ('tablename_sleeve_socket', 'ele_muffe'),
        'station':          ('tablename_ds_station', 'ele_ds_station'),
        'transformer':      ('tablename_ds_transformer', 'ele_ds_transformer'),
        'transition':       ('tablename_ds_inout', 'ele_ds_uebergang'),
    }
}

#: GEONIS field name mappings (English - German) for each solution.
#: Currently, the mappings are only available for the electric solution (ELE) and are not exhaustive.
GNFIELDS = {
    GNMEDIA_ELECTRIC: {
        'cable_ref':        ('fieldname_cable_ref', 'kabel_ref'),
        'code':             ('fieldname_code_ref', 'code'),
        'dd_ref':           ('fieldname_ds_ref', 'ds_ref'),
        'ddhv_ref':         ('fieldname_dshs_ref', 'dshs_ref'),
        'ddlv_ref':         ('fieldname_dsns_ref', 'dsns_ref'),
        'ddmv_ref':         ('fieldname_dsms_ref', 'dsms_ref'),
        'ddpl_ref':         ('fieldname_dsob_ref', 'dsob_ref'),
        'index':            ('fieldname_idx', 'idx'),
        'item_number':      ('fieldname_clamp_number', 'nummer'),
        'length':           ('fieldname_length', 'laenge'),
        'name_number':      ('fieldname_ds_trafo_name_number', 'name_nummer'),
        'pipe_ref':         ('fieldname_pipe_ref', 'rohr_ref'),
        'position':         ('fieldname_posnum', 'posnum'),
        'route_index':      ('fieldname_trench_idx', 'trasse_idx'),
        'route_pos':        ('fieldname_trench_pos', 'trasse_pos'),
        'route_ref':        ('fieldname_route_ref', 'trasse_ref'),
        'station_ref':      ('fieldname_station_ref', 'station_ref'),
        'strand_ref':       ('fieldname_strang_ref', 'strang_ref'),
        'transformer_ref':  ('fieldname_trafo_ref', 'trafo_ref'),
        'type':             ('fieldname_trasse_typ', 'typ'),
        'voltage':          ('fieldname_dense', 'spannung'),
    }
}
