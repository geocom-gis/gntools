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

import pytest

from gpf.paths import Workspace
from gntools.plans import *


@pytest.mark.parametrize('arg', [None, '', 1, 'PW', '7'])
def test_gnplanhelper_bad(arg):
    with pytest.raises(ValueError):
        PlanHelper(arg)


@pytest.mark.parametrize("test_input, name, fds, fc1, fc2, field, abbr", [
    ('pw7', 'PW7', 'ELE_PW7', 'ELE_PW7_KABEL', 'AWK_PW7_HALTUNG', 'TRASSE_REF7', 'PW'),
    (('pw1000', None, {'user_prefix': 'USR'}),
     'USR_PW1000', 'USR_ELE_PW1000', 'USR_ELE_PW1000_KABEL', 'USR_AWK_PW1000_HALTUNG', 'USR_TRASSE_REF1000', 'PW'),
    (('pw1', r'C:/temp/test.gdb', {}),
     'PW1', 'C:\\temp\\test.gdb\\ELE_PW1', 'C:\\temp\\test.gdb\\ELE_PW1\\ELE_PW1_KABEL',
     'C:\\temp\\test.gdb\\SEW_PW1\\AWK_PW1_HALTUNG', 'TRASSE_REF1', 'PW'),
    (('pw2', Workspace(r'C:/temp/test.gdb'), {}),
     'PW2', 'C:\\temp\\test.gdb\\ELE_PW2', 'C:\\temp\\test.gdb\\ELE_PW2\\ELE_PW2_KABEL',
     'C:\\temp\\test.gdb\\SEW_PW2\\AWK_PW2_HALTUNG', 'TRASSE_REF2', 'PW'),
    ('U_PW7', 'PW7', 'ELE_PW7', 'ELE_PW7_KABEL', 'AWK_PW7_HALTUNG', 'TRASSE_REF7', 'PW'),
    ('pw1000', 'U_PW1000', 'U_ELE_PW1000', 'U_ELE_PW1000_KABEL', 'U_AWK_PW1000_HALTUNG', 'U_TRASSE_REF1000', 'PW'),
    ('u_pw1000', 'U_PW1000', 'U_ELE_PW1000', 'U_ELE_PW1000_KABEL', 'U_AWK_PW1000_HALTUNG', 'U_TRASSE_REF1000', 'PW'),
    ('GP1001', 'U_GP1001', 'U_ELE_GP1001', 'U_ELE_GP1001_KABEL', 'U_AWK_GP1001_HALTUNG', 'U_TRASSE_REF1001', 'GP'),
])
def test_gnplanhelper_good(test_input, name, fds, fc1, fc2, field, abbr):
    if isinstance(test_input, tuple):
        ph = PlanHelper(test_input[0], test_input[1], **test_input[2])
    else:
        ph = PlanHelper(test_input)
    assert str(ph) == name
    assert repr(ph) == '{}({!r})'.format(PlanHelper.__name__, name.split('_')[-1])
    assert ph.get_feature_dataset('ele') == fds
    assert ph.get_feature_dataset('ELE') == fds
    assert ph.get_feature_class('ele', 'u_kabel') == fc1
    assert ph.get_feature_class('ELE', 'ele_kabel') == fc1
    assert ph.get_feature_class('sew', 'awk_haltung') == fc2
    assert '{}TRASSE_REF{}'.format(ph.prefix, ph.number) == field
    assert ph.abbreviation == abbr
