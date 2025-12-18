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


class CellRendererText(Gtk.CellRendererText):

    def __init__(self):
        super(CellRendererText, self).__init__()
        self.connect('editing-started', self.__class__.on_editing_started)

    def on_editing_started(self, editable, path):
        pass


class CellRendererTextCompletion(CellRendererText):

    def __init__(self, set_completion):
        super(CellRendererTextCompletion, self).__init__()
        self.set_completion = set_completion

    def on_editing_started(self, editable, path):
        super().on_editing_started(editable, path)
        self.set_completion(editable, path)


GObject.type_register(CellRendererText)
GObject.type_register(CellRendererTextCompletion)
