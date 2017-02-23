"""
Unit tests for edx_data.py.
"""
from __future__ import absolute_import, unicode_literals

from django.test import TestCase

from edx_salesforce import edx_data
from edx_salesforce.tests import edx_sample_data
from edx_salesforce.tests.mixins import DatabaseMixin


class EdxDataTests(DatabaseMixin, TestCase):
    """
    Test cases for edx_data.py
    """

    def setUp(self):
        super(EdxDataTests, self).setUp()
        self.site_domain = 'fake-site-domain.com'
        self.orgs = ['testX']
        self.usernames = ['fake-user1', 'fake-user2']

    @classmethod
    def setUpTestData(cls):
        super(EdxDataTests, cls).setUpTestData()

    def test_fetch_order_data(self):
        """
        Test _fetch_order_data for given organizations
        """
        actual = edx_data._fetch_order_data(self.orgs)  # pylint: disable=protected-access
        self.assertListEqual(actual, edx_sample_data.ORDER_DATA)

    def test_fetch_users_for_site(self):
        """
        Test _fetch_users_for_site for given site-domain
        """
        actual = edx_data._fetch_users_for_site(self.site_domain)   # pylint: disable=protected-access
        self.assertListEqual(actual, edx_sample_data.SITE_USERS)

    def test_fetch_language_preference_data(self):
        """
        Test _fetch_users_for_site for given site-domain
        """
        actual = edx_data._fetch_language_preference_data(self.usernames)   # pylint: disable=protected-access
        self.assertListEqual(actual, edx_sample_data.LANGUAGE_PREF_DATA)

    def test_fetch_user_profile_data(self):
        """
        Test _fetch_user_data for given username
        """
        actual = edx_data._fetch_user_data(self.usernames)  # pylint: disable=protected-access
        self.assertListEqual(actual, edx_sample_data.USER_PROFILE_DATA)

    def test_fetch_tracking_data(self):
        """
        Test _fetch_tracking_data for given username
        """
        actual = edx_data._fetch_tracking_data(self.usernames)  # pylint: disable=protected-access
        self.assertListEqual(actual, edx_sample_data.TRACKING_DATA)

    def test_fetch_user_data(self):
        """
        Test fetch_user_data for given username
        """
        actual = edx_data.fetch_user_data(self.site_domain, self.orgs)
        self.assertListEqual(actual, edx_sample_data.USER_DATA)
