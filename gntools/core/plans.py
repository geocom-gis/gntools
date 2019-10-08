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

import gpf.common.textutils as _tu
import gpf.common.validate as _vld
import gpf.tools.workspace as _ws


class PlanHelper:
    """
    PlanHelper(plan, {workspace}, {user_prefix})

    Helper class that returns proper names for *Generalized Plan* (*GP* or *Planwelt*)
    feature datasets, feature classes and field names.
    The generated names conform to the GEONIS conventions, i.e. if a plan name contains a number >= 1000, it is assumed
    that the plan is a custom user plan, which means that it will be prefixed with a *U_*.

    :param plan:            GEONIS Generalized Plan (Planwelt) name.
                            For user plans (where numeric part >= 1000), the *U_* prefix can be omitted
                            if the field names should **not** have this prefix.
    :param workspace:       An optional Esri workspace path (``str``) or a
                            :class:`gpf.tools.workspace.WorkspaceManager` instance.
                            When specified, the :func:`get_feature_class` and :func:`get_feature_dataset` functions
                            will return full paths instead of just the names.
    :keyword user_prefix:   The prefix for custom user plans (where numeric part >= 1000). Defaults to *U*.
    :type plan:             str, unicode
    :type workspace:        str, unicode, gpf.tools.workspace.WorkspaceManager
    :type user_prefix:      str, unicode

    If you initialize the ``PlanHelper`` with a workspace, full paths will be returned:

        >>> gph = PlanHelper('pw3', r'C:/temp/test.gdb')
        >>> gph.get_feature_dataset('was')
        'C:\\temp\\test.gdb\\WAS_PW3'
        >>> gph.get_feature_class('sew', 'haltung')
        'C:\\temp\\test.gdb\\SEW_PW3\\SEW_PW3_HALTUNG'
        >>> gph.get_feature_class('sew', 'awk_haltung')  # note: you can include a prefix override!
        'C:\\temp\\test.gdb\\SEW_PW3\\AWK_PW3_HALTUNG'
        >>> gph.get_field_name('MyField')
        'MYFIELD3'

    The following example shows how to use a ``PlanHelper`` for custom user plans (names only):

        >>> gph = PlanHelper('gp1000')
        >>> gph.get_feature_dataset('ELE')
        'U_ELE_GP1000'
        >>> gph.get_feature_class('ele', 'cable')
        'U_ELE_GP1000_CABLE'

    For custom plan field names, adding the *U_* prefix upon initialization will add it to the field name only:

        >>> gph = PlanHelper('pw1001')      # Initialize a PlanHelper for a custom plan without the U_ prefix
        >>> gph.get_feature_dataset('was')  # Custom plans will always have a U_ prefix for feature datasets and classes
        'U_ELE_PW1001'
        >>> gph.get_field_name('MyField')   # But by default, the U_ prefix will **not** be added to field names
        'MYFIELD1000'
        >>> gph = PlanHelper('u_pw1002')  # Now we deliberately add the U_ prefix
        >>> gph.get_feature_dataset('was')  # This does not affect feature dataset and feature class names
        'U_ELE_PW1002'
        >>> gph.get_field_name('MyField')   # But it does affect the field name
        'U_MYFIELD1000'

    """

    __ARG_PFX = 'user_prefix'
    __PLAN_SEP = _tu.UNDERSCORE
    __USER_PFX = 'U'

    def __init__(self, plan, workspace=None, **kwargs):

        self._gpn = _tu.EMPTY_STR
        self._num = _tu.EMPTY_STR
        self._pfx = _tu.EMPTY_STR
        self._wsman = None
        self._pfx_fields = False

        if workspace:
            self._wsman = workspace if isinstance(workspace, _ws.WorkspaceManager) \
                else _ws.WorkspaceManager(workspace)

        self._parse(plan, kwargs.get(self.__ARG_PFX, self.__USER_PFX).upper())

    def _parse(self, plan, user_prefix):
        """ Parses the plan, sets the plan parameters and validates them. """

        _vld.pass_if(_vld.is_text(plan, False), ValueError, "'plan' argument must be a string")

        parts = plan.upper().split(self.__PLAN_SEP)

        self._pfx_fields = user_prefix == parts[0]
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
        return self._wsman.construct(*parts)

    @_uppercase
    def _fds_name(self, fds_base):
        """ Returns the Generalized Plan name for a base feature dataset name. """
        return _tu.EMPTY_STR.join((self._pfx, fds_base, self.__PLAN_SEP, self._gpn, self._num))

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
            return fds_name, _tu.EMPTY_STR.join((fds_name, self.__PLAN_SEP, fc_parts[-1]))

        # replace first part with GP name prefix and join all parts
        fc_parts[0] = self._fds_name(fc_parts[0])
        return fds_name, self.__PLAN_SEP.join(fc_parts)

    def get_feature_dataset(self, fds_base):
        """
        Returns a feature dataset name for the current *Generalized Plan/Planwelt*.

        :param fds_base:    Case-insensitive base name (GEONIS Solution) of the feature dataset, e.g. *ELE*, *WAS* etc.
        :rtype:             str, unicode
        """
        fds_name = self._fds_name(fds_base)
        return fds_name if not self._wsman else self._make_path(fds_name)

    def get_feature_class(self, fds_base, fc_base):
        """
        Returns a feature class name for the current *Generalized Plan/Planwelt*.

        :param fds_base:    Case-insensitive base name (GEONIS Solution) of the parent feature dataset, e.g. *ELE*.
        :param fc_base:     Case-insensitive base name of the feature class, e.g. *(ELE_)KABEL*.
                            If *fc_base* already contains *fds_base* as a prefix, it will be replaced.
        :rtype:             str, unicode
        """
        fds_name, fc_name = self._fc_name(fds_base, fc_base)
        return fc_name if not self._wsman else self._make_path(fds_name, fc_name)

    @_uppercase
    def get_field_name(self, field_base):
        """
        Returns a field name for the current *Generalized Plan/Planwelt*.

        :param field_base:  Case-insensitive base name of the field, e.g. *TRASSE_REF*.
        :rtype:             str, unicode
        """
        return _tu.EMPTY_STR.join((self._pfx if self._pfx_fields else _tu.EMPTY_STR, field_base, self._num))

    def __repr__(self):
        """ Returns a representation of the PlanHelper. """
        return '{}({!r})'.format(PlanHelper.__name__, _tu.EMPTY_STR.join((self._gpn, self._num)))

    def __str__(self):
        """ Returns the (formatted) Generalized Plan (Planwelt) name. """
        return _tu.EMPTY_STR.join((self._pfx, self._gpn, self._num))
