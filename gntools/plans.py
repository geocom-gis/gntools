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
Module that facilitates working with GEONIS Generalized Plans (*GP* or *"Planwelt"*).
"""

import gntools.common.const as _const
import gpf.common.textutils as _tu
import gpf.common.validate as _vld
import gpf.paths as _paths


class PlanHelper:
    """
    PlanHelper(plan, {workspace}, {user_prefix})

    Helper class that returns proper names for *Generalized Plan* (*GP* or *Planwelt*)
    feature datasets, feature classes and field names.
    The generated names conform to the GEONIS conventions, i.e. if a plan name contains a number >= 1000, it is assumed
    that the plan is a custom user plan, which means that it will be prefixed with a *U_*.

    **Params:**

    -   **plan** (str, unicode):

        GEONIS Generalized Plan (Planwelt) name.
        For user plans (where numeric part >= 1000), the *U_* prefix can be omitted
        if the field names should **not** have this prefix.

    -   **workspace** (str, unicode, gpf.paths.Workspace):

        An optional Esri workspace path (``str``) or a :class:`gpf.paths.Workspace` instance.
        When specified, the :func:`get_feature_class` and :func:`get_feature_dataset` functions
        will return full paths instead of just the names.
        
    **Keyword params:**
    
    -   **user_prefix** (str, unicode):

        The prefix for custom user plans (where numeric part >= 1000). Defaults to *U*.

    If you initialize the ``PlanHelper`` with a workspace, full paths will be returned:

        >>> gph = PlanHelper('pw3', r'C:/temp/test.gdb')
        >>> gph.get_feature_dataset('was')
        'C:\\temp\\test.gdb\\WAS_PW3'
        >>> gph.get_feature_class('sew', 'haltung')
        'C:\\temp\\test.gdb\\SEW_PW3\\SEW_PW3_HALTUNG'
        >>> gph.get_feature_class('sew', 'awk_haltung')  # note: you can include a prefix override!
        'C:\\temp\\test.gdb\\SEW_PW3\\AWK_PW3_HALTUNG'

    The following example shows how to use a ``PlanHelper`` for custom user plans (names only):

        >>> gph = PlanHelper('gp1000')
        >>> gph.get_feature_dataset('ELE')
        'U_ELE_GP1000'
        >>> gph.get_feature_class('ele', 'cable')
        'U_ELE_GP1000_CABLE'
    """

    __ARG_PFX = 'user_prefix'
    __PLAN_SEP = _const.CHAR_UNDERSCORE
    __USER_PFX = 'U'

    def __init__(self, plan, workspace=None, **kwargs):

        self._gpn = _const.CHAR_EMPTY   # GP abbreviation (e.g. "GP", "PW" etc.)
        self._num = _const.CHAR_EMPTY   # GP number (e.g. 1, 2, 3, 1001 etc.)
        self._pfx = _const.CHAR_EMPTY   # User prefix with underscore (e.g. "U_")
        self._workspace = None          # Reference to the Workspace

        if workspace:
            self._workspace = workspace if isinstance(workspace, _paths.Workspace) else _paths.Workspace(workspace)

        self._parse(plan, kwargs.get(self.__ARG_PFX, self.__USER_PFX).upper())

    def _parse(self, plan, user_prefix):
        """ Parses the plan, sets the plan parameters and validates them. """

        _vld.pass_if(_vld.is_text(plan, False), ValueError, "'plan' argument must be a string")

        parts = plan.upper().split(self.__PLAN_SEP)

        self._gpn = _tu.get_alphachars(parts[-1])
        self._num = _tu.get_digits(parts[-1])

        _vld.pass_if(self._gpn, ValueError, "'plan' argument must start with one or more characters (e.g. 'PW')")
        _vld.pass_if(self._num, ValueError, "'plan' argument must contain a number")

        if int(self._num) >= 1000:
            self._pfx = user_prefix + self.__PLAN_SEP

    def _uppercase(*func):
        """
        Decorator to make sure all `func` string arguments are turned into upper case.
        """

        def func_wrapper(self, *args):
            args = (x.upper() if _vld.is_text(x) else x for x in args)
            return func[-1](self, *args)

        return func_wrapper

    def _make_path(self, *parts):
        return self._workspace.make_path(*parts)

    @_uppercase
    def _fds_name(self, fds_base):
        """ Returns the Generalized Plan name for a base feature dataset name. """
        return _const.CHAR_EMPTY.join((self._pfx, fds_base, self.__PLAN_SEP, self._gpn, self._num))

    @_uppercase
    def _fc_name(self, fds_base, fc_base):
        """ Returns the Generalized Plan names for a base feature dataset and feature class name. """
        fds_name = self._fds_name(fds_base)
        fc_parts = fc_base.split(self.__PLAN_SEP)

        if fc_parts[0] in (self.__USER_PFX, self._pfx.rstrip(self.__PLAN_SEP)):
            # remove U prefix if present
            fc_parts = fc_parts[1:]

        num_parts = len(fc_parts)
        if num_parts == 1 or fc_parts[0] == fds_base:
            # fc_base is a single word or it starts with fds_base
            return fds_name, _const.CHAR_EMPTY.join((fds_name, self.__PLAN_SEP, fc_parts[-1]))

        # replace first part with GP name prefix and concat all parts
        fc_parts[0] = self._fds_name(fc_parts[0])
        return fds_name, self.__PLAN_SEP.join(fc_parts)

    def get_feature_dataset(self, fds_base):
        """
        Returns a feature dataset name for the current *Generalized Plan/Planwelt*.

        :param fds_base:    Case-insensitive base name (GEONIS Solution) of the feature dataset, e.g. *ELE*, *WAS* etc.
        :rtype:             str, unicode
        """
        fds_name = self._fds_name(fds_base)
        return fds_name if not self._workspace else self._make_path(fds_name)

    def get_feature_class(self, fds_base, fc_base):
        """
        Returns a feature class name for the current *Generalized Plan/Planwelt*.

        :param fds_base:    Case-insensitive base name (GEONIS Solution) of the parent feature dataset, e.g. *ELE*.
        :param fc_base:     Case-insensitive base name of the feature class, e.g. *(ELE_)KABEL*.
                            If *fc_base* already contains *fds_base* as a prefix, it will be replaced.
        :rtype:             str, unicode
        """
        fds_name, fc_name = self._fc_name(fds_base, fc_base)
        return fc_name if not self._workspace else self._make_path(fds_name, fc_name)

    @property
    def abbreviation(self):
        """
        Returns the Generalized Plan abbreviation (e.g. "GP" or "PW").

        :rtype: str
        """
        return self._gpn

    @property
    def number(self):
        """
        Returns the Generalized Plan number as a string (e.g. "1", "2", "1001" etc.).

        :rtype: str
        """
        return self._num

    @property
    def prefix(self):
        """
        Returns the Generalized Plan user prefix including the separator (underscore), e.g. ``U_``.

        :rtype: str
        """
        return self._pfx

    @property
    def workspace(self):
        """
        Returns the Workspace instance for this PlanHelper (specified on initialization).

        :rtyoe: gpf.paths.Workspace
        """
        return self._workspace

    def __repr__(self):
        """ Returns a representation of the PlanHelper. """
        return '{}({!r})'.format(PlanHelper.__name__, _const.CHAR_EMPTY.join((self._gpn, self._num)))

    def __str__(self):
        """ Returns the (formatted) Generalized Plan (Planwelt) name. """
        return _const.CHAR_EMPTY.join((self._pfx, self._gpn, self._num))
