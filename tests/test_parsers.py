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

import sys
from collections import OrderedDict

import pytest

from gpf.paths import Workspace
from gntools.parsers import *


# noinspection PyTypeChecker
def test_eval():
    assert eval_arg('#', {}) == {}
    assert eval_arg({}, None) is None
    assert eval_arg('{}', {}) == {}
    assert eval_arg('123', 0) == 123
    assert eval_arg("['test', 1, 2, 3]", []) == ['test', 1, 2, 3]
    with pytest.raises(TypeError):
        eval_arg('{}', 0)


def test_clean():
    assert clean_arg('#', '') == ''
    assert clean_arg('#', None) is None
    assert clean_arg(3.14, 0) == 3.14
    assert clean_arg([], None) == []
    assert clean_arg('#test', '') == '#test'


def test_menuargparser_bad():
    sys.argv = []
    with pytest.raises(AttributeError):
        MenuArgParser()
    sys.argv = [__file__, 'workspace', 'qualifier', '#', '#', '#', '#']
    with pytest.raises(IndexError):
        MenuArgParser('Field0', 'Field1', 'Field2', 'Field3')


# noinspection PyProtectedMember
def test_menuargparser_basic():
    sys.argv = [__file__, 'workspace', 'qualifier', '#', 1, 2]
    menu_params = MenuArgParser('Field0', 'Field1')
    assert menu_params.workspace == Workspace('workspace', 'qualifier')
    assert repr(menu_params.arguments) == 'ScriptParameters(Field0=1, Field1=2)'
    assert menu_params.project_vars == {}
    assert menu_params._store == OrderedDict((
        ('script path', __file__),
        ('workspace path', 'workspace'),
        ('database qualifier', 'qualifier'),
        ('project variables', {}),
        ('script parameters', (1, 2))
    ))
    assert str(menu_params) == 'Script path: {}\n' \
                               'Workspace path: workspace\n' \
                               'Database qualifier: qualifier\n' \
                               'Script parameters: (Field0=1, Field1=2)'.format(__file__)


# noinspection PyUnresolvedReferences
def test_menuargparser_all():
    sys.argv = [__file__, 'workspace', 'qualifier']
    menu_params = MenuArgParser()
    assert menu_params.script == __file__
    assert menu_params.workspace == Workspace('workspace', 'qualifier')
    assert menu_params.arguments == (), 'arguments should be an empty tuple'
    assert menu_params.project_vars == {}, 'gv_vars should be an empty dictionary'

    sys.argv = [__file__, 'workspace', 'qualifier', '#', '#', '#', '#']
    menu_params = MenuArgParser()
    assert menu_params.script == __file__
    assert menu_params.workspace == Workspace('workspace', 'qualifier')
    assert menu_params.arguments == (), 'arguments should be an empty tuple'
    assert menu_params.project_vars == {}, 'gv_vars should be an empty dictionary'

    menu_params = MenuArgParser('Field0', 'Field1')
    assert menu_params.arguments == (None, None), 'arguments should be a tuple with 2 None values'
    assert menu_params.project_vars == {}, 'gv_vars should be an empty dictionary'
    menu_params_str = 'Script path: {}\n' \
                      'Workspace path: workspace\n' \
                      'Database qualifier: qualifier\n' \
                      "Script parameters: (Field0=None, Field1=None)".format(__file__)
    assert str(menu_params) == menu_params_str

    sys.argv = [__file__, 'workspace', 'qualifier', '#', '#', '#', 'last']
    with pytest.warns(ParameterWarning):
        menu_params = MenuArgParser('Field0', 'Field1')
    assert menu_params.arguments == (None, None), 'arguments should be a tuple with 2 None values'

    sys.argv = [__file__, 'workspace', 'qualifier', '#', 'a']
    menu_params = MenuArgParser('Field0', 'Field1', 'Field2')
    assert menu_params.arguments.Field0 == 'a', 'first script argument value should be "a"'
    assert menu_params.arguments == ('a', None, None), 'arguments should be a tuple with 3 values'
    menu_params_str = 'Script path: {}\n' \
                      'Workspace path: workspace\n' \
                      'Database qualifier: qualifier\n' \
                      "Script parameters: (Field0='a', Field1=None, Field2=None)".format(__file__)
    assert str(menu_params) == menu_params_str

    sys.argv = [__file__, 'workspace', 'qualifier', '#', 'a', 'b', 'c']
    menu_params = MenuArgParser()
    assert menu_params.arguments == ('a', 'b', 'c'), 'arguments should be a tuple with 3 values'
    menu_params_str = 'Script path: {}\n' \
                      'Workspace path: workspace\n' \
                      'Database qualifier: qualifier\n' \
                      "Script parameters: ('a', 'b', 'c')".format(__file__)
    assert str(menu_params) == menu_params_str

    sys.argv = [__file__, 'workspace', 'qualifier', '#', 'a', '#', '"b"']
    menu_params = MenuArgParser('Field0', 'Field1', 'Field2')
    assert menu_params.arguments.Field0 == 'a'
    assert menu_params.arguments.Field1 is None, 'single # chars must be removed'
    assert menu_params.arguments.Field2 == 'b', 'additional quotes must be stripped'

    sys.argv = [__file__, 'workspace', 'qualifier', '{"test": 1}', 'a', '"b"', "'#c'", 'omit']
    menu_params = MenuArgParser('Field0', 'Field1', 'Field2')
    assert menu_params.arguments == ('a', 'b', '#c')
    assert menu_params.project_vars == {'test': 1}
    menu_params_str = 'Script path: {}\n' \
                      'Workspace path: workspace\n' \
                      'Database qualifier: qualifier\n' \
                      "Project variables: {{'test': 1}}\n" \
                      "Script parameters: (Field0='a', Field1='b', Field2='#c')".format(__file__)
    assert str(menu_params) == menu_params_str


def test_formargparser_bad():
    sys.argv = [__file__, 'workspace', 'qualifier']
    with pytest.raises(AttributeError):
        FormArgParser()


# noinspection PyUnresolvedReferences, PyProtectedMember
def test_formargparser_all():
    sys.argv = [__file__, 'workspace', 'qualifier', 'table', 'key', 'value', '{"test": 1}', 'a']
    form_params = FormArgParser('Field0')
    assert form_params.script == __file__
    assert form_params._store == OrderedDict((
        ('script path', __file__),
        ('workspace path', 'workspace'),
        ('database qualifier', 'qualifier'),
        ('dataset name', 'table'),
        ('dataset ID field', 'key'),
        ('dataset ID value', 'value'),
        ('project variables', {"test": 1}),
        ('script parameters', ('a',))
    ))
    assert form_params.table == 'table'
    assert form_params.key_field == 'key'
    assert form_params.field_value == 'value'
    assert form_params.arguments.Field0 == 'a'
    assert form_params.project_vars == {'test': 1}
    form_params_str = 'Script path: {}\n' \
                      'Workspace path: workspace\n' \
                      'Database qualifier: qualifier\n' \
                      'Dataset name: table\n' \
                      'Dataset ID field: key\n' \
                      'Dataset ID value: value\n' \
                      "Project variables: {{'test': 1}}\n" \
                      "Script parameters: (Field0='a')".format(__file__)
    assert str(form_params) == form_params_str
