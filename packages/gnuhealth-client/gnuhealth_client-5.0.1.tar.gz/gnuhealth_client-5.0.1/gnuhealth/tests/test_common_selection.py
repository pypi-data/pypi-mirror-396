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
from unittest import TestCase

from gnuhealth.common.selection import freeze_value


class SelectionTestCase(TestCase):
    "Test common selection"

    def test_freeze_value(self):
        "Test freeze_value"
        self.assertEqual(freeze_value({'foo': 'bar'}), (('foo', 'bar'),))
        self.assertEqual(freeze_value([1, 42, 2, 3]), (1, 42, 2, 3))
        self.assertEqual(freeze_value('foo'), 'foo')
        self.assertEqual(
            freeze_value({'foo': {'bar': 42}}), (('foo', (('bar', 42),)),))
