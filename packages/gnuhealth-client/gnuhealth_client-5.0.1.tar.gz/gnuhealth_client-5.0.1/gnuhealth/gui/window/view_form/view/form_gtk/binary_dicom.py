#########################################################################
#             GNU HEALTH HOSPITAL MANAGEMENT - GTK CLIENT               #
#                      https://www.gnuhealth.org                        #
#########################################################################
#       The GNUHealth HMIS client based on the Tryton GTK Client        #
#########################################################################
#
# SPDX-FileCopyrightText:  2024 - Wei Zhao <wei.zhao@uclouvain.be>
# SPDX-License-Identifier: GPL-3.0-or-later
#
#
# This file is part of GNU Health.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.


import gettext
from urllib.request import urlopen
from urllib.parse import unquote

from gi.repository import Gtk

from gnuhealth.common import common
from gnuhealth.common import file_selection
from gnuhealth.common.entry_position import reset_position
from gnuhealth.gui.window.view_form.view.form_gtk.binary \
    import Binary, BinaryMixin

_ = gettext.gettext


# The binary_dicom widget is based on the existing binary widget of
# tryton.

class BinaryDicomMixin(BinaryMixin):

    def __init__(self, view, attrs):
        """
        Initialize the BinaryDicomMixin.

        :param view: The view parameter.
        :param attrs: The attrs parameter.
        """
        super(BinaryDicomMixin, self).__init__(view, attrs)
        self.filename = attrs.get('filename')

    @property
    def filters(self):
        """
        Get the list of filters to apply when selecting files.
        Return a list of Gtk.FileFilter objects.
        """
        filter_all = Gtk.FileFilter()
        filter_all.set_name(_('All files'))
        filter_all.add_pattern("*")
        filter_dicom = Gtk.FileFilter()
        filter_dicom.set_name(_('DICOM files'))
        filter_dicom.add_pattern("*.dcm")
        filter_dicom.add_pattern("*.DCM")
        filter_dicom.add_pattern("*.zip")
        filter_dicom.add_pattern("*.gz")
        return [filter_dicom, filter_all]

    def update_buttons(self, value):
        """
        Updates the visibility of buttons based on the input value.
        """
        if value:
            # self.but_save_as.show()    # don't show "save as" button
            self.but_select.hide()
            self.but_clear.show()
        else:
            self.but_save_as.hide()
            self.but_select.show()
            self.but_clear.hide()

    def select(self, widget=None):
        """
        Selects files from the file system and sets their URIs.
        """
        if not self.field:
            return
        filenames = file_selection(
            _('Select'),
            preview=self.preview,
            filters=self.filters,
            multi=True)
        if filenames:
            uris = [filename.as_uri() for filename in filenames]
            self._set_uris(uris)

    def select_drag_data_received(self, selection):
        """
        Handle the data received when an item is
        dragged and dropped onto the widget.
        """
        if not self.field:
            return
        self._set_uris(selection.get_uris())

    def _set_uris(self, uris):
        # put the data of all files (and the length of the files)
        # into a bytearray.
        # the format is:
        #   1. the bytes 'M', 'U', 'L', 'T' (ASCII 77,85,76,84)
        #   2. 8 bytes containing the length of the file (Little Endian)
        #   3. the data of the file
        #   4. repeat steps 2 and 3 for next file
        all_data = bytearray([77, 85, 76, 84])
        for uri in uris:
            uri = unquote(uri)
            data = urlopen(uri).read()
            # size in little endian 8 bytes
            all_data.extend(len(data).to_bytes(8, byteorder='little'))
            all_data.extend(data)
        # set the content of the field in the wizard
        self.field.set_client(self.record, all_data)
        if self.filename_field:
            self.filename_field.set_client(self.record, len(all_data))


# This is the dedicated widget for uploading DICOM files.  It allows
# multiple selection. It can read the DICOM files, the zipped DICOM
# files (.zip, .gz)

class BinaryDicom(BinaryDicomMixin, Binary):
    "BinaryDicom"

    def __init__(self, view, attrs):
        """
        Initializes the BinaryDicom class with the given view and attrs.

        Parameters:
            view: The view parameter.
            attrs: The attrs parameter.

        Returns:
            None
        """
        super(BinaryDicom, self).__init__(view, attrs)

        self.widget = Gtk.HBox(spacing=0)
        self.wid_size = Gtk.Entry()
        self.wid_size.set_width_chars(self.default_width_chars)
        self.wid_size.set_alignment(1.0)
        self.wid_size.props.sensitive = False
        if self.filename and attrs.get('filename_visible'):
            self.wid_text = Gtk.Entry()
            self.wid_text.set_property('activates_default', True)
            self.wid_text.connect('focus-out-event',
                                  lambda x,
                                  y: self._focus_out())
            self.wid_text.connect_after('key_press_event', self.sig_key_press)
            self.wid_text.connect('icon-press', self.sig_icon_press)
            self.widget.pack_start(
                self.wid_text, expand=True, fill=True, padding=0)
        else:
            self.wid_text = None
        self.mnemonic_widget = self.wid_text
        self.widget.pack_start(
            self.wid_size, expand=not self.filename, fill=True, padding=0)

        self.widget.pack_start(
            self.toolbar(), expand=False, fill=False, padding=0)

    def sig_icon_press(self, widget, icon_pos):
        """
        This function handles the press event for the signal icon.
        It takes in the widget, icon position, and event as parameters.
        """
        widget.grab_focus()
        if icon_pos == Gtk.EntryIconPosition.PRIMARY:
            self.open_()

    def display(self):
        """
        Displays the BinaryDicom object on the screen.
        """
        super(BinaryDicom, self).display()
        if not self.field:
            if self.wid_text:
                self.wid_text.set_text('')
            self.wid_size.set_text('')
            self.but_save_as.hide()
            return False
        if hasattr(self.field, 'get_size'):
            size = self.field.get_size(self.record)
        else:
            size = len(self.field.get(self.record))
        self.wid_size.set_text(common.humanize(size or 0))
        reset_position(self.wid_size)
        if self.wid_text:
            self.wid_text.set_text(self.filename_field.get(self.record) or '')
            reset_position(self.wid_text)
            if size:
                icon, tooltip = 'gnuhealth-open', _("Open...")
            else:
                icon, tooltip = None, ''
            pos = Gtk.EntryIconPosition.PRIMARY
            if icon:
                pixbuf = common.IconFactory.get_pixbuf(
                    icon, Gtk.IconSize.MENU)
            else:
                pixbuf = None
            self.wid_text.set_icon_from_pixbuf(pos, pixbuf)
            self.wid_text.set_icon_tooltip_text(pos, tooltip)
        self.update_buttons(bool(size))
        return True
