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
from .integer import Integer


class Float(Integer):
    "Float"

    @property
    def digits(self):
        if self.field and self.record:
            return self.field.digits(self.record, factor=self.factor)

    @property
    def width(self):
        digits = self.digits
        if digits:
            return sum(digits)
        else:
            return self.attrs.get('width', 18)

    def display(self):
        digits = self.digits
        if digits:
            self.entry.digits = digits[1]
        else:
            self.entry.digits = None
        super(Float, self).display()
