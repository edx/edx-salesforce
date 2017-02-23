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

        users_with_attrs = {}
        user_ids = []
        with connections['default'].cursor() as cursor:
            query= "SELECT auth_user.id, auth_user.username, auth_user.email" \
                   " FROM auth_user, student_userattribute" \
                   " WHERE auth_user.id=student_userattribute.user_id" \
                   " AND student_userattribute.name='created_on_site'" \
                   " AND student_userattribute.value='{domain}';".format(
                domain=site_domain
            )
            cursor.execute(query)
            auth_users = cursor.fetchall()

            for auth_user in auth_users:
                users_with_attrs[auth_user[0]] = {
                    'auth_user.username': auth_user[1],
                    'auth_user.email': auth_user[2],
                }
                user_ids.append(auth_user[0])

            for user_id in users_with_attrs:
                query = "SELECT name, value FROM student_userattribute" \
                        " WHERE (user_id = {user_id}" \
                        " AND name IN ('utm_source', 'utm_medium', 'utm_campaign'," \
                        " 'utm_term', 'utm_content'));".format(
                    user_id = user_id
                )
                cursor.execute(query)
                user_attrs = cursor.fetchall()
                for user_attr_name, user_attr_value in user_attrs:
                    users_with_attrs[user_id]["student_userattribute." + user_attr_name] = user_attr_value


            query = "SELECT user_id, name, country, year_of_birth, language" \
                    " FROM auth_userprofile" \
                    " WHERE user_id IN ({user_id_list})".format(
                user_id_list = ','.join(map(str, user_ids))
            )
            cursor.execute(query)
            user_profile_attrs = cursor.fetchall()
            for user_id, name, country, year_of_birth, language in user_profile_attrs:
                users_with_attrs[user_id]["auth_userprofile.name"] = name
                users_with_attrs[user_id]["auth_userprofile.country"] = country
                users_with_attrs[user_id]["auth_userprofile.year_of_birth"] = year_of_birth
                users_with_attrs[user_id]["auth_userprofile.language"] = language

            self.stdout.write(str(users_with_attrs))

            self.stdout.write('edxapp query')
        with connections['ecommerce'].cursor() as cursor:
            # cursor.execute()
            self.stdout.write('ecommerce query')
