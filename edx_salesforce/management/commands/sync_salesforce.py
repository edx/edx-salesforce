from django.core.management.base import BaseCommand, CommandError
from django.db import connections


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

        with connections['default'].cursor() as cursor:
            # cursor.execute()
            self.stdout.write('edxapp query')
        with connections['ecommerce'].cursor() as cursor:
            # cursor.execute()
            self.stdout.write('ecommerce query')
