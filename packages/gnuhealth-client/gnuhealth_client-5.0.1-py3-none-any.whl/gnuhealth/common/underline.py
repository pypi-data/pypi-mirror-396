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
from gi.repository import Gdk


def find_hardware_keycode(string):
    keymap = Gdk.Keymap.get_for_display(Gdk.Display.get_default())
    for i, c in enumerate(string):
        found, keys = keymap.get_entries_for_keyval(
            Gdk.unicode_to_keyval(ord(c)))
        if found:
            return i
    return -1


def set_underline(label):
    "Set underscore for mnemonic accelerator"
    label = label.replace('_', '__')
    position = find_hardware_keycode(label)
    if position >= 0:
        label = label[:position] + '_' + label[position:]
    return label
