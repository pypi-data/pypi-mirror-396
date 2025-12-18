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
"Board"
import gettext
import xml.dom.minidom

from gnuhealth.common import MODELNAME, RPCExecute
from gnuhealth.gui import Main
from gnuhealth.gui.window.view_board import ViewBoard

from .tabcontent import TabContent

_ = gettext.gettext


class Board(TabContent):
    'Board'

    def __init__(self, model, name='', **attributes):
        super(Board, self).__init__(**attributes)

        context = attributes.get('context')
        self.view_id, = attributes.get('view_ids')

        view = RPCExecute(
            'model', 'ir.ui.view', 'view_get', self.view_id, context=context)

        xml_dom = xml.dom.minidom.parseString(view['arch'])
        root, = xml_dom.childNodes
        self.board = ViewBoard(root, context=context)
        self.model = model
        self.dialogs = []
        if not name:
            name = MODELNAME.get(model)
        self.name = name

        self.create_tabcontent()
        self.board.reload()

    def get_toolbars(self):
        return {}

    def widget_get(self):
        return self.board.widget_get()

    def sig_reload(self, test_modified=True):
        self.board.reload()
        return True

    def sig_close(self):
        return True

    def compare(self, model, attributes):
        if not attributes:
            return False
        return (
            self.model == model
            and self.attributes.get('view_ids') == attributes.get('view_ids')
            and self.attributes.get('context') == attributes.get('context'))

    def __hash__(self):
        return id(self)

    def sig_win_close(self, widget):
        Main().sig_win_close(widget)

    def set_cursor(self):
        if not self.board.actions:
            return
        first_action = self.board.actions[0]
        first_action.screen.set_cursor()
