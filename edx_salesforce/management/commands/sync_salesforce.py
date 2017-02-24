from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):
    help = 'Synchronize the user account data for the given site/organization with a Salesforce account'

    users_with_attrs = {}
    user_ids = []

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

    def _fetch_from_auth_user(self, cursor, site_domain):
        query = "SELECT auth_user.id, auth_user.username, auth_user.email" \
                " FROM auth_user, student_userattribute" \
                " WHERE auth_user.id=student_userattribute.user_id" \
                " AND student_userattribute.name='created_on_site'" \
                " AND student_userattribute.value='{domain}';".format(
            domain=site_domain
        )
        cursor.execute(query)
        auth_users = cursor.fetchall()

        for user_id, username, email in auth_users:
            self.users_with_attrs[user_id] = {
                'auth_user.username': username,
                'auth_user.email': email,
            }
            self.user_ids.append(user_id)

    def _fetch_from_auth_userprofile(self, cursor, user_ids_str):
        query = "SELECT user_id, name, country, year_of_birth, language" \
                " FROM auth_userprofile" \
                " WHERE user_id IN ({user_id_list})".format(
            user_id_list=user_ids_str
        )
        cursor.execute(query)
        user_profile_attrs = cursor.fetchall()
        for user_id, name, country, year_of_birth, language in user_profile_attrs:
            self.users_with_attrs[user_id]["auth_userprofile.name"] = name
            self.users_with_attrs[user_id]["auth_userprofile.country"] = country
            self.users_with_attrs[user_id]["auth_userprofile.year_of_birth"] = year_of_birth
            self.users_with_attrs[user_id]["auth_userprofile.language"] = language

    def _fetch_from_student_userattribute(self, cursor, user_ids_str):
        query = "SELECT user_id, name, value FROM student_userattribute" \
                " WHERE (user_id IN ({user_id_list})" \
                " AND name IN ('utm_source', 'utm_medium', 'utm_campaign'," \
                " 'utm_term', 'utm_content'));".format(
            user_id_list=user_ids_str
        )
        cursor.execute(query)
        user_attrs = cursor.fetchall()
        for user_id, user_attr_name, user_attr_value in user_attrs:
            self.users_with_attrs[user_id]["student_userattribute." + user_attr_name] = user_attr_value

    def handle(self, *args, **options):
        site_domain = options['site_domain']
        orgs = options['orgs']

        self.stdout.write('Syncing user account data for site {site} and orgs {orgs}...'.format(
            site=site_domain,
            orgs=','.join(orgs)
        ))

        with connections['default'].cursor() as cursor:
            self._fetch_from_auth_user(cursor, site_domain)

            if self.user_ids:
                user_ids_str = ','.join(map(str, self.user_ids))
                self._fetch_from_auth_userprofile(cursor, user_ids_str)
                self._fetch_from_student_userattribute(cursor, user_ids_str)

            self.stdout.write(str(self.users_with_attrs))

            self.stdout.write('edxapp query')
        with connections['ecommerce'].cursor() as cursor:
            # cursor.execute()
            self.stdout.write('ecommerce query')
