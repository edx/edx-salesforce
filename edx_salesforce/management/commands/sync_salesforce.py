from django.core.management.base import BaseCommand, CommandError

from edx_salesforce.edx_data import fetch_user_data


class Command(BaseCommand):
    help = 'Synchronize the user account data for the given site/organization with a Salesforce account'

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

        self.stdout.write('Syncing user account data for site {site} and orgs {orgs}...'.format(
            site=site_domain,
            orgs=','.join(orgs)
        ))

        data = fetch_user_data(site_domain, orgs)
