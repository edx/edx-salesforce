"""
The module contains a data structure used to load test data
for the edxapp and ecommerce database schemas.
"""

from __future__ import absolute_import, unicode_literals


DATA = {
    'default': {
        'auth_user': {
            'columns': ('id', 'password', 'last_login', 'is_superuser', 'username', 'first_name', 'last_name', 'email',
                        'is_staff', 'is_active', 'date_joined'),
            'records': (
                (1, '"fake"', '"2016-01-01 11:11:11"', 0, '"fake-user1"', '"fake1"', '"user"',
                 '"fake-user1@fake.email"', 0, 1, '"2016-01-01 11:11:11"'),
                (2, '"fake"', '"2016-01-01 11:11:11"', 0, '"fake-user2"', '"fake2"', '"user"',
                 '"fake-user2@fake.email"', 0, 1, '"2016-01-01 11:11:11"'),
            )
        },
        'auth_userprofile': {
            'columns': ('id', 'name', 'language', 'year_of_birth', 'country', 'goals', 'level_of_education', 'gender',
                        'user_id'),
            'records': (
                (1, '"fake user1"', '"en"', 1990, '"US"', '"test-goals"', '"p"', '"m"', 1),
                (2, '"fake user2"', '"en"', 1980, '"US"', '"test-goals"', '"a"', '"f"', 2),
            )
        },
        'student_userattribute': {
            'columns': ('id', 'name', 'value', 'user_id'),
            'records': (
                (1, '"created_on_site"', '"fake-site-domain.com"', 1),
                (2, '"registration_utm_campaign"', '"fake_registration_utm_campaign"', 1),
                (3, '"registration_utm_medium"', '"fake_registration_utm_medium"', 1),
                (4, '"registration_utm_source"', '"fake_registration_utm_source"', 1),
                (5, '"registration_utm_term"', '"fake_registration_utm_term"', 1),
                (6, '"registration_utm_content"', '"fake_registration_utm_content"', 1),
                (7, '"created_on_site"', '"fake-site-domain.com"', 2),
                (8, '"registration_utm_campaign"', '"test_registration_utm_campaign"', 2),
                (9, '"registration_utm_medium"', '"test_registration_utm_medium"', 2),
                (10, '"registration_utm_source"', '"test_registration_utm_source"', 2),
                (11, '"registration_utm_term"', '"test_registration_utm_term"', 2),
                (12, '"registration_utm_content"', '"test_registration_utm_content"', 2),
            )
        },
        'user_api_userpreference': {
            'columns': ('id', '`key`', 'value', 'user_id'),
            'records': (
                (1, '"pref-lang"', '"en"', 1),
                (2, '"pref-lang"', '"fr"', 2),
            )
        },
    },
    'ecommerce': {
        'catalogue_product': {
            'columns': ('id', 'course_id'),
            'records': (
                (1, '"course-v1:testX:fake-course-id1"'),
                (2, '"course-v1:testX:fake-course-id2"'),
            )
        },
        'ecommerce_user': {
            'columns': ('id', 'username'),
            'records': (
                (1, '"fake-user1"'),
                (2, '"fake-user2"'),
            )
        },
        'order_line': {
            'columns': (
                'id',
                'quantity',
                'line_price_before_discounts_incl_tax',
                'line_price_incl_tax',
                'order_id',
                'product_id'
            ),
            'records': (
                (1, 1, 2.22, 10.11, 1, 1),
                (2, 2, 4.44, 20.22, 2, 2),
            )
        },
        'order_order': {
            'columns': ('id', 'number', 'date_placed', 'user_id'),
            'records': (
                (1, '"ORDER-1"', '"2017-01-01 11:11:11"', 1),
                (2, '"ORDER-2"', '"2017-01-01 11:11:11"', 2),
            )
        },
        'voucher_voucher': {
            'columns': ('id', 'code'),
            'records': {
                (1, '"fake-code1"'),
                (2, '"fake-code2"'),
            }
        },
        'voucher_voucherapplication': {
            'columns': ('id', 'order_id', 'voucher_id'),
            'records': {
                (1, 1, 1),
                (2, 2, 2),
            }
        }
    }
}
