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
import gettext

from gnuhealth.gui.window.view_form.screen import Screen
from gnuhealth.gui.window.win_form import WinForm

_ = gettext.gettext


class Note(WinForm):
    "Note window"

    def __init__(self, record, callback=None):
        self.resource = '%s,%s' % (record.model_name, record.id)
        self.note_callback = callback
        title = _('Notes (%s)') % (record.rec_name())
        screen = Screen('ir.note', domain=[
            ('resource', '=', self.resource),
        ], mode=['tree', 'form'])
        super(Note, self).__init__(screen, self.callback, view_type='tree',
                                   title=title)
        screen.search_filter()

    def destroy(self):
        self.prev_view.save_width()
        super(Note, self).destroy()

    def callback(self, result):
        if result:
            unread = self.screen.group.fields['unread']
            for record in self.screen.group:
                if record.loaded or record.id < 0:
                    if 'unread' not in record.modified_fields:
                        unread.set_client(record, False)
            self.screen.save_current()
        if self.note_callback:
            self.note_callback()
