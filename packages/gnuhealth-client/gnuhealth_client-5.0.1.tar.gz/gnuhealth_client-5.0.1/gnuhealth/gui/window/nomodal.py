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
import gnuhealth.common as common


class NoModal(object):

    def __init__(self):
        self.parent = common.get_toplevel_window()
        self.sensible_widget = common.get_sensible_widget(self.parent)
        self.page = None
        self.parent_focus = []
        focus = self.parent.get_focus()
        while focus:
            self.parent_focus.append(focus)
            focus = focus.get_parent()

    def register(self):
        from gnuhealth.gui.main import Main
        main = Main()
        self.page = main.get_page()
        if not self.page:
            self.page = main
        self.page.dialogs.append(self)
        self.sensible_widget.props.sensitive = False

    def destroy(self):
        if not self.page:
            return
        self.page.dialogs.remove(self)
        self.parent.present()
        self.sensible_widget.props.sensitive = True
        for focus in self.parent_focus:
            if focus and focus.is_ancestor(self.parent):
                try:
                    focus.grab_focus()
                except TypeError:
                    # GooCanvas needs a GooCanvasItem
                    continue
                break

    def show(self):
        raise NotImplementedError

    def hide(self):
        raise NotImplementedError

    def default_size(self):
        from gnuhealth.gui.main import Main
        main = Main()
        allocation = main.window.get_allocation()
        width, height = allocation.width, allocation.height
        return max(width - 150, 0), max(height - 150, 0)
