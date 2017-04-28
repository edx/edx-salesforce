""" Django command for producing a CSV report of EdX user account data """

from __future__ import absolute_import, unicode_literals

import os
import time

import unicodecsv as csv

from django.conf import settings
from django.core.management.base import BaseCommand

from edx_salesforce.choices import COUNTRIES_BY_CODE, EDUCATION_BY_CODE
from edx_salesforce.edx_data import fetch_user_data

REPORT_HEADER = [
    'Email',
    'Username',
    'Full Name',
    'Country',
    'Year of Birth',
    'Language',
    'Level of Education',
    'Interest',
    'Registration Date',
    'UTM Campaign',
    'UTM Content',
    'UTM Source',
    'UTM Medium',
    'UTM Term',
    'Course Runs',
]


class Command(BaseCommand):
    """
    This command creates a CSV report containing user account data related to the given
    site and organizations. The organizations provided are used to find ecommerce orders
    made by users who may not have created their user accounts on the given site. The
    CSV file is written to the PROJECT_ROOT/output directory.
    """
    help = 'Produces CSV report containing user data related to the given site and organizations.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-s',
            '--site-domain',
            dest='site_domain',
            required=True,
            help='Domain of site for which user account data should be collected'
        )
        parser.add_argument(
            '-o',
            '--orgs',
            nargs='+',
            dest='orgs',
            required=True,
            help=(
                'Organizations for which user account data should be collected for '
                'course purchases associated with those organizations'
            )
        )

    def handle(self, *args, **options):
        site_domain = options['site_domain']
        orgs = options['orgs']

        users = fetch_user_data(site_domain, orgs)

        if not users:
            self.stdout.write(
                'No user accounts found for site {site} and orgs {orgs}...'.format(
                    site=site_domain,
                    orgs=','.join(orgs),
                )
            )
            return

        total_users = len(users)
        pluralize_total_users = '' if total_users == 1 else 's'
        org_count = len(orgs)
        pluralize_orgs = '' if org_count == 1 else 's'

        self.stdout.write(
            'Running user account report for {total_users} user account{pluralize_total_users} '
            'for site {site} and org{pluralize_orgs} {orgs}...'.format(
                total_users=total_users,
                pluralize_total_users=pluralize_total_users,
                site=site_domain,
                pluralize_orgs=pluralize_orgs,
                orgs=','.join(orgs),
            )
        )

        output_filename = '{directory}/user_accounts_{site}_{timestamp}.csv'.format(
            directory=self._output_dir(),
            site=site_domain,
            timestamp=time.strftime('%Y%m%d-%H%M%S')
        )

        with open(output_filename, 'wb') as csvfile:  # pylint: disable=open-builtin
            writer = csv.writer(csvfile, delimiter=str(','))
            writer.writerow(REPORT_HEADER)
            for user in users:
                writer.writerow([
                    user['email'],
                    user['username'],
                    user['full_name'],
                    COUNTRIES_BY_CODE.get((user['country'] or '').upper()),
                    user['year_of_birth'],
                    settings.LANGUAGES_BY_CODE.get(user['language']),
                    EDUCATION_BY_CODE.get((user['level_of_education'] or '').lower()),
                    user['goals'],
                    user['registration_date'].strftime('%Y-%m-%d'),
                    user['tracking'].get('utm_campaign', ''),
                    user['tracking'].get('utm_content', ''),
                    user['tracking'].get('utm_source', ''),
                    user['tracking'].get('utm_medium', ''),
                    user['tracking'].get('utm_term', ''),
                    ' '.join([c['course_id'] for c in user['courses']]),
                ])

        self.stdout.write(
            'Finished running user account report for {total_users} user{pluralize_total_users} '
            'for site {site} and org{pluralize_orgs} {orgs}.'.format(
                total_users=total_users,
                pluralize_total_users=pluralize_total_users,
                site=site_domain,
                orgs=','.join(orgs),
                pluralize_orgs=pluralize_orgs,
            )
        )

    def _output_dir(self):
        """
        Returns the report output directory name. Creates the directory if it doesn't exist.
        """
        output_dir = '{root}/output'.format(root=settings.PROJECT_ROOT)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return output_dir
