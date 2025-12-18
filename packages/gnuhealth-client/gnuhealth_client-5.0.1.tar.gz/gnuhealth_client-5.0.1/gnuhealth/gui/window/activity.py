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


from gnuhealth.config import GNUHEALTH_ICON
from gi.repository import Gtk


class Activity():
    "GNU Health client Activity Logger"
    activity_window = Gtk.Window()
    activity_window.set_default_size(500, 500)
    activity_window.set_title("Activity log - GNU Health ")
    activity_window.set_icon(GNUHEALTH_ICON)

    sw = Gtk.ScrolledWindow()
    sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

    # TextView
    activity = Gtk.TextView()
    sw.add(activity)

    # Make it read-only
    activity.set_editable(False)
    textbuffer = activity.get_buffer()

    activity_window.add(sw)
