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

This module also contains GEONIS definition mappings (`GNTABLES` and `GNFIELDS`, for example).
These mappings are stored as dictionary structures.
Mapping structures determine which Python Definition property/attribute is mapped to what GEONIS definition
(e.g. table or field name). When a language-based or custom override is available, the definition override is looked up
in the definition table for a certain solution, which is stored in the database. If this table does not exist,
or no override was found, the default (German) value is returned instead.

A mapping should always have the following dictionary structure::

    mapping_name = {
      solution_name1: {
          code_property_name1: (definition_table_property_name, default_definition_value),
          code_property_name2: (..., ...),
          ...
      },
      solution_name2: {
          ...
      }
    }

If no definition table property name (i.e. lookup key) is available, it should be set to ``None``.
Default definition values should always have a value, so that any failed lookup immediately returns this value.
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
GNFIELD_REL_TYPE = 'relate_type'
GNFIELD_REL_CARDINAL = 'relate_cardinal'
GNFIELD_REL_TABLE_REL = 'relate_table'
GNFIELD_REL_TABLE_SRC = 'source_table'
GNFIELD_REL_TABLE_DST = 'target_table'
GNFIELD_REL_KEYFIELD_SRC = 'source_idfield'
GNFIELD_REL_KEYFIELD_DST = 'target_reffield'
GNFIELD_REL_RELFIELD_SRC = 'relate_sourcereffield'
GNFIELD_REL_RELFIELD_DST = 'relate_targetreffield'

# GEONIS description fields
GNFIELD_DESC_CUSTOM = 'description_custom'
GNFIELD_DESC_DE = 'description_g'
GNFIELD_DESC_EN = 'description_e'
GNFIELD_DESC_FR = 'description_f'
GNFIELD_DESC_IT = 'description_i'

# GEONIS relationship type names
GNRELTYPE_AGGREGRATE = 'Aggregate'
GNRELTYPE_COMPOSITE = 'Composite'
GNRELTYPE_DATALINK = 'Data_Link'
GNRELTYPE_ENTITY = 'Entity'
GNRELTYPE_LABEL = 'Label'
GNRELTYPE_PLAN = 'Plan'
GNRELTYPE_RELATE = 'Relate'
GNRELTYPE_SHAPEGROUP = 'Shape_Group'

# Default GEONIS media/solution (feature dataset) names
GNMEDIA_STANDARD = 'std'
GNMEDIA_GENERAL = 'div'
GNMEDIA_ELECTRIC = 'ele'
GNMEDIA_WATER = 'was'
GNMEDIA_GAS = 'gas'
GNMEDIA_SEWER = 'sew'
GNMEDIA_HEATING = 'fwa'
GNMEDIA_CADASTRE = 'av'
