#########################################################################
#             GNU HEALTH HOSPITAL MANAGEMENT - GTK CLIENT               #
#                      https://www.gnuhealth.org                        #
#########################################################################
#       The GNUHealth HMIS client based on the Tryton GTK Client        #
#########################################################################
#
# SPDX-FileCopyrightText: 2008-2024 The Tryton Community <info@tryton.org>
# SPDX-FileCopyrightText: 2017-2024 GNU Health Community <info@gnuhealth.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# This file is part of GNU Health.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import locale
import gi

# Settings for the GNU Health client and server versions
__version__ = "5.0.1"
SERVER_VERSION = "7.0.0"


gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_foreign('cairo')
try:
    gi.require_version('GtkSpell', '3.0')
except ValueError:
    pass
try:
    gi.require_version('EvinceDocument', '3.0')
    gi.require_version('EvinceView', '3.0')
except ValueError:
    pass

"""
try:
    # Import earlier otherwise there is a segmentation fault on MSYS2
    import goocalendar  # noqa: F401
except ImportError:
    pass
"""

if not hasattr(locale, 'localize'):
    def localize(formatted, grouping=False, monetary=False):
        if '.' in formatted:
            seps = 0
            parts = formatted.split('.')
            if grouping:
                parts[0], seps = locale._group(parts[0], monetary=monetary)
            decimal_point = locale.localeconv()[
                monetary and 'mon_decimal_point' or 'decimal_point']
            formatted = decimal_point.join(parts)
            if seps:
                formatted = locale._strip_padding(formatted, seps)
        else:
            seps = 0
            if grouping:
                formatted, seps = locale._group(formatted, monetary=monetary)
            if seps:
                formatted = locale._strip_padding(formatted, seps)
        return formatted
    setattr(locale, 'localize', localize)


def delocalize(string, monetary=False):
    conv = locale.localeconv()

    # First, get rid of the grouping
    ts = conv[monetary and 'mon_thousands_sep' or 'thousands_sep']
    if ts:
        string = string.replace(ts, '')
    # next, replace the decimal point with a dot
    dd = conv[monetary and 'mon_decimal_point' or 'decimal_point']
    if dd:
        string = string.replace(dd, '.')
    return string


setattr(locale, 'delocalize', delocalize)
