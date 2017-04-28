"""
Unit tests for run_user_account_report management command.
"""
from __future__ import absolute_import, unicode_literals

import glob
import os
import shutil

import mock

from django.conf import settings
from django.core.management import CommandError, call_command
from django.test import TestCase

from edx_salesforce.tests.edx_sample_data import USER_DATA


class TestUserAccountReport(TestCase):
    """
    Test run_user_account_report management command.
    """

    def setUp(self):
        super(TestUserAccountReport, self).setUp()

        self.orgs = ['testX', 'TestB']
        self.site_domain = 'test_server.fake_domain'
        self.output_directory_path = '{root}/output'.format(root=settings.PROJECT_ROOT)

    def _remove_output_directory(self):
        """
        Removes the output directory/
        """
        # Intentionally not calling from setUp.
        shutil.rmtree(self.output_directory_path, ignore_errors=True)

    def _get_output_directory(self):
        """
        Returns list of existing files in given directory.
        """
        return glob.glob(
            '{output_directory}/user_accounts_{site}_*.csv'.format(
                output_directory=self.output_directory_path,
                site=self.site_domain
            )
        )

    @mock.patch('edx_salesforce.management.commands.run_user_account_report.fetch_user_data')
    def test_command_with_user_data(self, mock_user_fetch_data):
        """
        Test management command with user data and check if csv file exists.
        """
        self._remove_output_directory()
        mock_user_fetch_data.return_value = USER_DATA
        call_command(
            'run_user_account_report',
            '--site-domain', self.site_domain,
            '--orgs', self.orgs
        )
        output_directory = self._get_output_directory()

        # Output directory will have only one file.
        self.assertEqual(len(output_directory), 1)

        # is file exist in output directory
        self.assertTrue(os.path.isfile(output_directory[0]))

    @mock.patch('edx_salesforce.management.commands.run_user_account_report.fetch_user_data')
    def test_command_with_user_data_with_output_directory(self, mock_user_fetch_data):
        """
        Test management command with user data and check if csv file exists.
        """
        mock_user_fetch_data.return_value = USER_DATA
        call_command(
            'run_user_account_report',
            '--site-domain', self.site_domain,
            '--orgs', self.orgs
        )
        output_directory = self._get_output_directory()

        # is file exist in output directory
        self.assertTrue(os.path.isfile(output_directory[0]))

    @mock.patch('edx_salesforce.management.commands.run_user_account_report.fetch_user_data')
    def test_command_without_user_data(self, mock_user_fetch_data):
        """
        Test management command without user data and output directory should be empty.
        """
        self._remove_output_directory()
        mock_user_fetch_data.return_value = []
        call_command(
            'run_user_account_report',
            '--site-domain', self.site_domain,
            '--orgs', self.orgs
        )
        output_directory = self._get_output_directory()

        # Output directory will be empty.
        self.assertEqual(len(output_directory), 0)

    def test_command_with_invalid_arguments(self):
        """
        Test management command raises CommandError with invalid argument.
        """

        # raises CommandError without --site-domain argument.
        with self.assertRaises(CommandError):
            call_command(
                'run_user_account_report',
                '--orgs', self.orgs
            )

        # raises CommandError without --orgs argument.
        with self.assertRaises(CommandError):
            call_command(
                'run_user_account_report',
                '--site-domain', self.site_domain,
            )

        # raises CommandError without --site-domain and --orgs arguments.
        with self.assertRaises(CommandError):
            call_command(
                'run_user_account_report'
            )
