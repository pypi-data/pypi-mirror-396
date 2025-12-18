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

try:
    from http import HTTPStatus
except ImportError:
    from http import client as HTTPStatus

from gi.repository import Gtk

from gnuhealth.common import (
    IconFactory, RPCException, play_sound, process_exception)
from gnuhealth.common.underline import set_underline
from gnuhealth.config import CONFIG, GNUHEALTH_ICON
from gnuhealth.exceptions import GNUHealthServerError
from gnuhealth.gui import Main
from gnuhealth.gui.window.nomodal import NoModal

_ = gettext.gettext


class CodeScanner(NoModal):

    def __init__(self, callback, loop=False):
        super().__init__()
        self.callback = callback
        self.loop = loop
        self.dialog = Gtk.MessageDialog(
            transient_for=self.parent, destroy_with_parent=True,
            text=_("Code Scanner"))
        Main().add_window(self.dialog)
        self.dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.dialog.set_icon(GNUHEALTH_ICON)
        self.dialog.connect('response', self.response)

        self.dialog.set_title(_("Code Scanner"))

        self.entry = Gtk.Entry()
        self.entry.set_activates_default(True)
        self.entry.set_placeholder_text(_("Code"))
        self.dialog.get_message_area().pack_start(
            self.entry, expand=False, fill=False, padding=9)

        button_close = self.dialog.add_button(
            set_underline(_("Close")), Gtk.ResponseType.CLOSE)
        button_close.set_image(IconFactory.get_image(
            'gnuhealth-close', Gtk.IconSize.BUTTON))

        button_ok = self.dialog.add_button(
            set_underline(_("OK")), Gtk.ResponseType.OK)
        button_ok.set_image(IconFactory.get_image(
            'gnuhealth-ok', Gtk.IconSize.BUTTON))
        self.dialog.set_default_response(Gtk.ResponseType.OK)

        self.dialog.show_all()
        self.register()
        self.entry.grab_focus()

    def _play(self, sound):
        if CONFIG['client.code_scanner_sound']:
            play_sound(sound)

    def response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            code = self.entry.get_text()
            self.entry.set_text('')
            if code:
                while True:
                    try:
                        modified = self.callback(code)
                        self._play('success')
                        if not self.loop or not modified:
                            self.destroy()
                    except Exception as exception:
                        unauthorized = (
                            isinstance(exception, GNUHealthServerError)
                            and exception.faultCode == str(
                                int(HTTPStatus.UNAUTHORIZED)))
                        if not unauthorized:
                            self._play('danger')
                        try:
                            process_exception(exception)
                        except RPCException:
                            pass
                        if unauthorized:
                            continue
                        self.destroy()
                    return
        if not self.loop or response != Gtk.ResponseType.OK:
            self.destroy()

    def destroy(self):
        super().destroy()
        self.dialog.destroy()

    def show(self):
        self.dialog.show()

    def hide(self):
        self.dialog.hide()
