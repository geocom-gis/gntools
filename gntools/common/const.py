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

# GEONIS system tables
GNTABLE_VERSION = 'GN_VERSION'
GNTABLE_LOOKUP = 'GN_LOOKUP'
GNTABLE_RELATION_DEF = 'GNREL_DEFINITION'
GNTABLE_RELATION_RULE = 'GNREL_RULE'
GNTABLE_RELATION_FORMULA = 'GNREL_FORMULA'
GNTABLE_SPLITMERGE = 'GN_SPLITMERGE_DEF'

# Default GEONIS media/feature dataset names
GNMEDIA_STANDARD = 'STD'
GNMEDIA_GENERAL = 'DIV'
GNMEDIA_ELECTRIC = 'ELE'
GNMEDIA_WATER = 'WAS'
GNMEDIA_GAS = 'GAS'
GNMEDIA_SEWER = 'SEW'
GNMEDIA_HEATING = 'FWA'
GNMEDIA_CADASTRE = 'AV'
