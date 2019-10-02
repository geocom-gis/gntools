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
The *core* subpackage contains a set of general classes and functions
to improve the overall GEONIS Python experience.

One of the most notable classes is the :class:`gntools.core.protocol.ProtocolLogger`,
which can be used to write messages and features to a GEONIS XML log file (or *Protocol*).
Users can read this file back in with GEONIS and click on features,
which is useful for inspection and/or validation purposes.

Also of interest might be the :py:mod:`gntools.core.params` submodule. This submodule contains classes that
help obtain passed-in arguments from GEONIS menu or form scripts in a standardized and user-friendly manner.
"""
