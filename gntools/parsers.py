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

import gntools.common.const as _const
import gpf.common.textutils as _tu
import gpf.common.validate as _vld
import gpf.paths as _paths

EMPTY_ARG = _const.CHAR_HASH


class ParameterWarning(UserWarning):
    """ Warning that is displayed when a (minor) issue occurred while parsing the script parameters. """
    pass


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

    def __init__(self, name, func=None, default=_const.CHAR_EMPTY, required=False):
        self.name = name
        self.default = default
        self.required = required
        if _vld.signature_matches(func, clean_arg):
            self.func = func
        else:
            if func:
                raise ValueError('Function requires {} input arguments'.format(clean_arg.func_code.co_argcount))
            self.func = clean_arg


class _BaseArgParser(object):
    """ Abstract base data class that stores the Python arguments for all GEONIS scripts. """

    __metaclass__ = _abc.ABCMeta
    __slots__ = ('_store', '_paramnames', '_paramtuple')

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

        if self._paramnames:
            # Declare a new ScriptParameters named tuple type and override its str() behavior
            typename = self._get_typename(self._PARAM_CONST)
            self._paramtuple = _ntuple(typename, field_names=param_names)
            self._paramtuple.__str__ = lambda x: repr(x).replace(typename, _const.CHAR_EMPTY)
        else:
            # Use a regular tuple type if no parameter names have been set
            self._paramtuple = tuple

    @_abc.abstractproperty
    def _mapping(self):
        return ()

    @staticmethod
    def _get_typename(value):
        """ Formats a text string like a class/type name (Pascal case), e.g. 'my type' becomes 'MyType'. """
        return value.title().replace(_const.CHAR_SPACE, _const.CHAR_EMPTY)

    def _save_params(self, values):
        """
        Validates and stores script parameters as a namedtuple (or regular tuple if param names are undefined).
        """
        num_values = len(values)
        num_params = len(self._paramnames)

        if num_params:
            # User has defined parameter names
            if num_values > num_params and any(values):
                # If there are more arguments (with a value) than parameter names, inform the user
                _warn('Number of {} exceeds the expected total of {}'.
                      format(self._PARAM_CONST, self._MAX_PARAMS), ParameterWarning)

            # Truncate or fill (with None) the number of parameters to the expected number
            # and return a new ScriptParameters namedtuple instance
            return self._paramtuple(*((values[i] if i < num_values else None) for i in range(num_params)))

        else:
            # No parameter names have been set by the user: populate and return a regular tuple for non-empty values
            return self._paramtuple(v for v in values if v)

    # noinspection PyProtectedMember, PyUnresolvedReferences
    def _parse(self):
        """ Reads the Python arguments specific to GEONIS menu scripts. """
        last_m = len(self._mapping) - 1
        for i, m in enumerate(self._mapping):
            try:
                if m.name == self._PARAM_CONST and i == last_m:
                    # If it's the last mapping for the script parameters,
                    # consume all remaining arguments and call mapping function on each script param.
                    # Note that there can not be more than self._MAX_PARAMS and superfluous parameters are removed.
                    value = self._save_params([m.func(x, m.default) for x in _sys.argv[i:i+self._MAX_PARAMS]])
                else:
                    # Call mapping function on the current argument
                    value = m.func(_sys.argv[i], m.default) or m.default
            except IndexError:
                value = m.default
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
        return self._store.get(self._SCRIPT_PATH, _const.CHAR_EMPTY)

    @property
    def workspace(self):
        """
        Returns a :class:`gpf.paths.Workspace` instance for the Esri workspace
        (and optionally a qualifier) specified in the script arguments.

        :rtype:    gpf.paths.Workspace
        """
        qualifier = self._store.get(self._DB_QUALIFIER, _const.CHAR_EMPTY)
        ws_path = self._store.get(self._WORKSPACE_PATH)
        return _paths.Workspace(ws_path, qualifier)

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

        :return:    A namedtuple or tuple with additional script arguments (if any).
        """
        return self._store.get(self._PARAMETERS, self._paramtuple(*(None for _ in self._paramnames)))

    def __repr__(self):
        """ Returns the representation of the current instance. """
        return '{}{}'.format(self.__class__.__name__, self._paramnames)

    def __str__(self):
        """
        Returns a formatted string of all instance properties (e.g. for logging purposes).

        :return str:    Formatted properties (1 per line).
        """

        # Filter out empty properties and format key-value pairs (1 per line)
        # Notice that ScriptParameters will have their type name removed, because its __str__ method has been overridden
        return _const.CHAR_LF.join('{}: {}'.format(_tu.capitalize(k), v)
                                   for k, v in self._store.iteritems() if _vld.has_value(v))


class MenuArgParser(_BaseArgParser):
    """
    Data class that reads and stores the Python arguments for GEONIS menu scripts.
    Simply instantiate this class in a menu-based Python script to get easy access to all arguments passed to it.

    Script argument values are cleaned before they are returned,
    which means that excessive single or double quotes will be removed.
    Furthermore, any "#" values (representing NoData placeholders) are replaced by ``None``
    and trailing NoData values are removed.

    Using the GEONIS menu definition (XML), a user can pass additional parameters to the script.
    These parameters do not have a name, but the ``MenuArgParser`` can name them for you
    if it is initialized with one or more parameter names, so you can access them as a
    `namedtuple <https://docs.python.org/2/library/collections.html#collections.namedtuple>`_.

    Example:

        >>> params = MenuArgParser('arg1', 'arg2')
        >>> params.arguments.arg1
        'This value has been set in the GEONIS menu XML'
        >>> params.arguments.arg2
        'This is another argument'

        >>> # Note that you can still get the arguments by index or unpack as a tuple
        >>> params.arguments[1]
        'This is another argument'
        >>> params.arguments == 'This value has been set in the GEONIS menu XML', 'This is another argument'
        True

    If you don't specify any parameter names, the ``arguments`` property returns a regular ``tuple``.

    **Params:**

    -   **param_names**:

        Optional parameter names to set on the parsed menu arguments.
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
            _ArgMap(self._PARAMETERS, default=None)  # 4, 5, 6
        )


class FormArgParser(_BaseArgParser):
    """
    Data class that reads and stores the Python arguments for GEONIS form scripts.
    Simply instantiate this class in a form-based Python script to get easy access to all arguments passed to it.

    Script argument values are cleaned before they are returned,
    which means that excessive single or double quotes will be removed.
    Furthermore, any "#" values (representing NoData placeholders) are replaced by ``None``
    and trailing NoData values are removed.

    Using the GEONIS form definition (XML), a user can pass additional parameters to the script.
    These parameters do not have a name, but the ``FormArgParser`` can name them for you
    if it is initialized with one or more parameter names, so you can access them as a
    `namedtuple <https://docs.python.org/2/library/collections.html#collections.namedtuple>`_.

    Example:

        >>> params = FormArgParser('arg1', 'arg2')
        >>> params.arguments.arg1
        'This value has been set in the GEONIS form XML'
        >>> params.arguments.arg2
        'This is another argument'

        >>> # Note that you can still get the arguments by index or unpack as a tuple
        >>> params.arguments[1]
        'This is another argument'
        >>> params.arguments == 'This value has been set in the GEONIS form XML', 'This is another argument'
        True

    If you don't specify any parameter names, the ``arguments`` property returns a regular ``tuple``.

    **Params:**
    
    -   **param_names**:

        Optional parameter names to set on the parsed form arguments.
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
            _ArgMap(self._PARAMETERS, default=None)  # 7, 8, 9
        )

    @property
    def table(self):
        """
        Table or feature class name to which the form script applies.

        :rtype: str
        """
        return self._store.get(self._TABLE_NAME, _const.CHAR_EMPTY)

    @property
    def key_field(self):
        """
        Field name that holds the key value (ID) for the feature/row to which the form script applies.

        :rtype: str
        """
        return self._store.get(self._KEY_FIELD, _const.CHAR_EMPTY)

    @property
    def field_value(self):
        """
        The value of the table key field name for the feature/row to which the form script applies.

        :rtype: str
        """
        return self._store.get(self._ID_VALUE)


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
