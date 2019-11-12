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
Module for GEONIS internationalization (i18n).
It reads the current GEONIS language code from the Windows registry.
When not found (or not set), the default language code for the current Windows locale is returned.
"""

import _winreg
from warnings import warn as _warn
from locale import getdefaultlocale as _getdeflocale

import const as _const

GN_LANG_EN = 'en'
GN_LANG_DE = 'de'
GN_LANG_FR = 'fr'
GN_LANG_IT = 'it'
GN_LANG_CUSTOM = 'cu'

_GN_REGKEY = 'Software\\geocom'
_GN_REGVAL = 'DefaultLanguage'


def _get_registry_lang():
    """
    Tries to find the GEONIS language in the Windows registry. Returns an empty string when not found.

    :rtype: basestring
    """

    try:
        # Connect to the Windows registry for the current user
        reg = _winreg.ConnectRegistry(None, _winreg.HKEY_CURRENT_USER)

        # Find and read the Software\geocom\DefaultLanguage key
        key = _winreg.OpenKey(reg, _GN_REGKEY)
        lang, _ = _winreg.QueryValueEx(key, _GN_REGVAL)

    except WindowsError:
        _warn('Failed to read GEONIS language setting from Windows registry')
        lang = ''

    return lang.lower()


def _get_locale_lang():
    """
    Returns the language from the default locale. When not set, an empty string is returned.

    :rtype: basestring
    """

    loc, _ = _getdeflocale()
    lang, _ = loc.lower().split(_const.CHAR_UNDERSCORE)
    if lang in (GN_LANG_DE, GN_LANG_EN, GN_LANG_FR, GN_LANG_IT):
        return lang

    _warn('Failed to determine a valid GEONIS language from Windows locale: defaulting to German')
    return ''


def get_language():
    """
    Returns the lowercase language code ('de', 'fr', 'en', or 'it') for the current GEONIS installation.

    If the language code could not be determined, or the language is not a supported GEONIS language
    (i.e. not English, German, French or Italian), the default language code ('de') is returned.

    .. note::   When the GEONIS user has specified a custom language, 'cu' is returned.
                This will affect the *description* field names that are returned by the
                :func:`gntools.definitions.DefinitionTable.fieldnames` object.
    """

    # Get language from registry or (when not set/found) from the locale or (when undefined) return German default
    return _get_registry_lang() or _get_locale_lang() or GN_LANG_DE
