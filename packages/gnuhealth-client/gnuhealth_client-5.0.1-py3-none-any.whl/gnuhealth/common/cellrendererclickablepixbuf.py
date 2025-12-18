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
from gi.repository import GObject, Gtk


class CellRendererClickablePixbuf(Gtk.CellRendererPixbuf):
    __gsignals__ = {
        'clicked': (GObject.SignalFlags.RUN_LAST, GObject.TYPE_NONE,
                    (GObject.TYPE_STRING, )),
    }

    def __init__(self):
        Gtk.CellRendererPixbuf.__init__(self)
        self.set_property('mode', Gtk.CellRendererMode.ACTIVATABLE)

    def do_activate(
            self, event, widget, path, background_area, cell_area, flags):
        self.emit('clicked', path)


GObject.type_register(CellRendererClickablePixbuf)
