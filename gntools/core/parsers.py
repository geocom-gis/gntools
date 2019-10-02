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
This module contains classes that help parse arguments for GEONIS menu or form-based Python scripts.
"""

import abc as _abc
import sys as _sys
from ast import literal_eval as _ast_eval
from collections import OrderedDict as _ODict
from collections import namedtuple as _ntuple
from warnings import warn as _warn

import gpf.common.textutils as _tu
import gpf.common.validate as _vld
import gpf.tools.workspace as _ws

EMPTY_ARG = _tu.HASH


def clean_arg(value, default):
    """
    Strips all trailing quotes and NoData (#) values from text.

    :param value:   The argument value that should be evaluated. If this is not a string, it will be passed as-is.
    :param default: The default value that should be returned if the value is a NoData string (#).
    """
    if isinstance(value, basestring):
        value = value.strip('"\'')
    return default if value == EMPTY_ARG else value


def eval_arg(value, default):
    """
    Evaluates a literal string as a Python object in a safe manner.

    :param value:       The string that should be evaluated. If it is not a string, the *default* value is returned.
    :param default:     The default value to return if evaluation failed.
    :type value:        str, unicode
    :raises TypeError:  When the evaluated object does not have the same type as the *default* value.
                        This error can only be raised when *default* is not ``None``.
    """
    try:
        obj = _ast_eval(value)
    except (ValueError, TypeError, SyntaxError):
        return default
    return_type = basestring if isinstance(default, basestring) else type(default)
    if default is not None and not isinstance(obj, return_type):
        raise TypeError('Argument value should evaluate to a {} (got {})'.
                        format(return_type.__name__, type(obj).__name__))
    return obj


class _ArgMap(object):
    """
    Argument mapping helper class for the argument parsers.

    :param name:        Descriptive name of the attribute to map to.
    :param func:        Function to run on the attribute value. Defaults to the :func:`clean_arg` method when not set.
                        Note that the function must accept 2 parameters: value and default.
    :param default:     Default to set when *func* fails or the value was not found. Defaults to an empty string.
    :param required:    When ``True``, the argument parser will raise a ``ValueError``.
                        Otherwise, the *default* will be used for the value, without raising an error.
    """

    __slots__ = ('name', 'default', 'func', 'required')

    def __init__(self, name, func=None, default=_tu.EMPTY_STR, required=False):
        self.name = name
        self.default = default
        self.required = required
        if callable(func):
            f = func
            req_args = clean_arg.func_code.co_argcount
            num_args = req_args
            if hasattr(func, 'im_func'):
                f = func.im_func
                num_args += 1
            if hasattr(f, 'func_code') and f.func_code.co_argcount == num_args:
                self.func = func
            else:
                raise ValueError('Argument function requires {} input arguments'.format(req_args))
        else:
            self.func = clean_arg
        self.func = func if callable(func) else clean_arg


class _BaseArgParser(object):
    """ Base data class that stores the Python arguments for all GEONIS scripts. """

    __metaclass__ = _abc.ABCMeta
    __slots__ = ('_store', '_paramnames', '_paramtype')

    _SCRIPT_PATH = 'script path'
    _WORKSPACE_PATH = 'workspace path'
    _DB_QUALIFIER = 'database qualifier'
    _PROJECT_VARS = 'project variables'
    _PARAMETERS = 'script parameters'

    # The maximum amount of PARAMETERS values that will be parsed/read from sys.argv
    _MAX_PARAMS = 3
    _PARAM_CONST = _PARAMETERS

    def __init__(self, *param_names):
        self._store = _ODict()
        self._paramnames = param_names
        _vld.pass_if(len(param_names) <= self._MAX_PARAMS, IndexError,
                     'There can be no more than {} custom parameters'.format(self._MAX_PARAMS))
        self._paramtype = _ntuple(self._format_typename(self._PARAM_CONST), param_names)

    @_abc.abstractproperty
    def _mapping(self):
        return ()

    @staticmethod
    def _format_typename(value):
        """ Formats a name as a class/type-like name. """
        return value.title().replace(_tu.SPACE, _tu.EMPTY_STR)

    def _save_params(self, values):
        """ Validates and stores script parameters as a namedtuple. """
        num_values = len(values)
        num_params = len(self._paramnames)
        if num_values > num_params:
            # If there are more than *num_params*, inform the user
            _warn('Number of {} exceeds the expected total of {}'.format(self._PARAM_CONST, self._MAX_PARAMS))
        # Truncate (and "zerofill") number of parameters to the number expected
        return self._paramtype(*((values[i] if i < num_values else None) for i in range(num_params)))

    # noinspection PyProtectedMember, PyUnresolvedReferences
    def _parse(self):
        """ Reads the Python arguments specific to GEONIS menu scripts. """
        last_m = len(self._mapping) - 1
        for i, m in enumerate(self._mapping):
            try:
                if m.name == self._PARAM_CONST and i == last_m:
                    # If it's the last mapping for the script parameters, allow multiple values up to param names length
                    value = self._save_params([m.func(x, None) for x in _sys.argv[i:]])
                else:
                    value = m.func(_sys.argv[i], m.default) or m.default
            except IndexError:
                value = m.default
            except TypeError:
                if m.name == self._PARAM_CONST and i == last_m:
                    value = self._paramtype(*(None for _ in self._paramnames))
                else:
                    raise
            except Exception:
                raise
            if m.required and not _vld.has_value(value, True):
                raise AttributeError('Empty or missing required {!r} argument at position {}'.format(m.name, i))
            self._store[m.name] = value

    @property
    def script(self):
        """
        The full path to the script that was called by the Python interpreter.

        :rtype:    str
        """
        return self._store.get(self._SCRIPT_PATH, _tu.EMPTY_STR)

    @property
    def workspace(self):
        """
        Returns a :class:`gpf.tools.workspace.WorkspaceManager` instance for the Esri workspace
        (and optionally a qualifier) specified in the script arguments.

        :rtype:    gpf.tools.workspace.WorkspaceManager
        """
        qualifier = self._store.get(self._DB_QUALIFIER, _tu.EMPTY_STR)
        ws_path = self._store.get(self._WORKSPACE_PATH)
        return _ws.WorkspaceManager(ws_path, qualifier)

    @property
    def project_vars(self):
        """
        Any optional GEONIS project variables passed to the script (often not used).

        :rtype:    dict
        """
        return self._store.get(self._PROJECT_VARS, {})

    @property
    def arguments(self):
        """
        Returns the arguments passed to the script (if defined in the GEONIS XML script configuration).

        :rtype:     tuple
        """
        return self._store.get(self._PARAMETERS, self._paramtype(*(None for _ in self._paramnames)))

    def __repr__(self):
        """ Returns the representation of the current instance. """
        return '{}{}'.format(self.__class__.__name__, self._paramnames)

    def __str__(self):
        """
        Returns a formatted string of all instance properties (e.g. for logging purposes).

        :return str:    Formatted properties (1 per line).
        """
        return _tu.LF.join('{}: {}'.format(_tu.capitalize(k), v) for
                           k, v in self._store.iteritems() if _vld.has_value(v)).replace(
                self._format_typename(self._PARAM_CONST), _tu.EMPTY_STR)


class MenuArgParser(_BaseArgParser):
    """
    Data class that reads and stores the Python arguments for GEONIS menu scripts.

    Simply instantiate this class in a menu-based Python script to get easy access to all arguments passed to it.
    """

    def __init__(self, *param_names):
        super(MenuArgParser, self).__init__(*param_names)
        self._parse()

    @property
    def _mapping(self):
        return (
            _ArgMap(self._SCRIPT_PATH),  # 0
            _ArgMap(self._WORKSPACE_PATH, required=True),  # 1
            _ArgMap(self._DB_QUALIFIER),  # 2
            _ArgMap(self._PROJECT_VARS, eval_arg, {}),  # 3
            _ArgMap(self._PARAMETERS)  # 4, 5, 6
        )


class FormArgParser(_BaseArgParser):
    """
    Data class that reads and stores the Python arguments for GEONIS form scripts.

    Simply instantiate this class in a form-based Python script to get easy access to all arguments passed to it.

    Script argument values are cleaned before they are returned,
    which means that excessive single or double quotes will be removed.
    Furthermore, any "#" values (representing NoData placeholders) are replaced by ``None``.
    """

    _TABLE_NAME = 'dataset name'
    _KEY_FIELD = 'dataset ID field'
    _ID_VALUE = 'dataset ID value'

    def __init__(self, *param_names):
        super(FormArgParser, self).__init__(*param_names)
        self._parse()

    @property
    def _mapping(self):
        return (
            _ArgMap(self._SCRIPT_PATH),  # 0
            _ArgMap(self._WORKSPACE_PATH, required=True),  # 1
            _ArgMap(self._DB_QUALIFIER),  # 2
            _ArgMap(self._TABLE_NAME, required=True),  # 3
            _ArgMap(self._KEY_FIELD, required=True),  # 4
            _ArgMap(self._ID_VALUE, required=True),  # 5
            _ArgMap(self._PROJECT_VARS, eval_arg, {}),  # 6
            _ArgMap(self._PARAMETERS)  # 7, 8, 9
        )

    @property
    def table(self):
        """
        Table or feature class name to which the form script applies.

        :rtype: str
        """
        return self._store.get(self._TABLE_NAME, _tu.EMPTY_STR)

    @property
    def key_field(self):
        """
        Field name that holds the key value (ID) for the feature/row to which the form script applies.

        :rtype: str
        """
        return self._store.get(self._KEY_FIELD, _tu.EMPTY_STR)

    @property
    def field_value(self):
        """
        The value of the table key field name for the feature/row to which the form script applies.

        :rtype: str
        """
        return self._store.get(self._ID_VALUE)
