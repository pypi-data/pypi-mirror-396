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

from gnuhealth.common import MODELACCESS
from gnuhealth.gui.window import Window

_ = gettext.gettext


def translate_view(datas):
    model = datas['model']
    Window.create(
        'ir.translation',
        res_id=False,
        domain=[('model', '=', model)],
        mode=['tree', 'form'],
        name=_('Translate view'))


def get_plugins(model):
    access = MODELACCESS['ir.translation']
    if access['read'] and access['write']:
        return [
            (_('Translate view'), translate_view),
            ]
    else:
        return []
