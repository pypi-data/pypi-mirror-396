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

from gnuhealth.common import humanize


class Humanize(TestCase):
    "Test humanize"

    def test_humanize(self):
        "Test humanize"
        for value, text in [
                (0, '0'),
                (1, '1'),
                (5, '5'),
                (10, '10'),
                (50, '50'),
                (100, '100'),
                (1000, '1000'),
                (1001, '1k'),
                (1500, '1.5k'),
                (1000000, '1000k'),
                (1000001, '1M'),
                (1010000, '1.01M'),
                (10**33, '1000Q'),
                (0.1, '0.1'),
                (0.5, '0.5'),
                (0.01, '0.01'),
                (0.05, '0.05'),
                (0.001, '1m'),
                (0.0001, '0.1m'),
                (0.000001, '1µ'),
                (0.0000015, '1.5µ'),
                (0.00000105, '1.05µ'),
                (0.000001001, '1µ'),
                (10**-33, '0.001q'),
        ]:
            with self.subTest(value=value):
                self.assertEqual(humanize(value), text)
            if value:
                value *= -1
                text = '-' + text
                with self.subTest(value=value):
                    self.assertEqual(humanize(value), text)
