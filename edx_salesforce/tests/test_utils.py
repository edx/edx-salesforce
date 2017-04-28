"""
Unit tests for edx_salesforce utility module.
"""

from __future__ import absolute_import, unicode_literals

from ddt import ddt, data, unpack
from django.test import TestCase

from edx_salesforce.utils import parse_user_full_name


@ddt
class TestUtils(TestCase):
    """
    Test utilities module.
    """

    @data(
        ('Foo Bar', ('Foo', 'Bar')),
        ('Bar', (None, 'Bar')),
        (' Foo  Bar ', ('Foo', 'Bar'))
    )
    @unpack
    def test_parse_user_full_name(self, full_name, expected):
        result = parse_user_full_name(full_name)
        self.assertEqual(expected, result)
