"""
Sample data to test edx_data.py
"""

from __future__ import absolute_import, unicode_literals
from datetime import datetime
from decimal import Decimal

SITE_USERS = [{'username': 'fake-user1'}, {'username': 'fake-user2'}]

LANGUAGE_PREF_DATA = [
    {
        'username': 'fake-user1',
        'language_preference': 'en'
    },
    {
        'username': 'fake-user2',
        'language_preference': 'fr'
    }
]

ORDER_DATA = [
    {
        'username': 'fake-user1',
        'order_id': 1,
        'quantity': 1,
        'list_price': Decimal('2.22'),
        'unit_price': Decimal('10.11'),
        'coupon_codes': ['fake-code1'],
        'purchase_date': datetime(2017, 1, 1, 11, 11, 11),
        'course_id': 'course-v1:testX:fake-course-id1'
    },
    {
        'username': 'fake-user2',
        'order_id': 2,
        'quantity': 2,
        'list_price': Decimal('4.44'),
        'unit_price': Decimal('20.22'),
        'coupon_codes': ['fake-code2'],
        'purchase_date': datetime(2017, 1, 1, 11, 11, 11),
        'course_id': 'course-v1:testX:fake-course-id2'
    }

]

USER_PROFILE_DATA = [
    {
        'username': 'fake-user1',
        'country': 'US',
        'year_of_birth': 1990,
        'full_name': 'fake user1',
        'email': 'fake-user1@fake.email',
        'goals': 'test-goals',
        'level_of_education': 'p',
        'gender': 'm',
        'registration_date': datetime(2016, 1, 1, 11, 11, 11)
    },
    {
        'username': 'fake-user2',
        'country': 'US',
        'year_of_birth': 1980,
        'full_name': 'fake user2',
        'email': 'fake-user2@fake.email',
        'goals': 'test-goals',
        'level_of_education': 'a',
        'gender': 'f',
        'registration_date': datetime(2016, 1, 1, 11, 11, 11)
    }
]

TRACKING_DATA = [
    {
        'username': 'fake-user1',
        'utm_param_name': 'registration_utm_campaign',
        'utm_param_value': 'fake_registration_utm_campaign'
    },
    {
        'username': 'fake-user1',
        'utm_param_name': 'registration_utm_medium',
        'utm_param_value': 'fake_registration_utm_medium'
    },
    {
        'username': 'fake-user1',
        'utm_param_name': 'registration_utm_source',
        'utm_param_value': 'fake_registration_utm_source'
    },
    {
        'username': 'fake-user1',
        'utm_param_name': 'registration_utm_term',
        'utm_param_value': 'fake_registration_utm_term'
    },
    {
        'username': 'fake-user1',
        'utm_param_name': 'registration_utm_content',
        'utm_param_value': 'fake_registration_utm_content'
    },
    {
        'username': 'fake-user2',
        'utm_param_name': 'registration_utm_campaign',
        'utm_param_value': 'test_registration_utm_campaign'
    },
    {
        'username': 'fake-user2',
        'utm_param_name': 'registration_utm_medium',
        'utm_param_value': 'test_registration_utm_medium'
    },
    {
        'username': 'fake-user2',
        'utm_param_name': 'registration_utm_source',
        'utm_param_value': 'test_registration_utm_source'
    },
    {
        'username': 'fake-user2',
        'utm_param_name': 'registration_utm_term',
        'utm_param_value': 'test_registration_utm_term'
    },
    {
        'username': 'fake-user2',
        'utm_param_name': 'registration_utm_content',
        'utm_param_value': 'test_registration_utm_content'
    }
]

USER_DATA = [
    {
        'username': 'fake-user1',
        'year_of_birth': 1990,
        'full_name': 'fake user1',
        'email': 'fake-user1@fake.email',
        'language': 'en',
        'country': 'US',
        'goals': 'test-goals',
        'level_of_education': 'p',
        'gender': 'm',
        'registration_date': datetime(2016, 1, 1, 11, 11, 11),
        'courses': [{
            'username': 'fake-user1',
            'list_price': Decimal('2.22'),
            'order_id': 1,
            'unit_price': Decimal('10.11'),
            'coupon_codes': ['fake-code1'],
            'purchase_date': datetime(2017, 1, 1, 11, 11, 11),
            'course_id': 'course-v1:testX:fake-course-id1',
            'quantity': 1
        }],
        'tracking': {
            'utm_campaign': 'fake_registration_utm_campaign',
            'utm_content': 'fake_registration_utm_content',
            'utm_medium': 'fake_registration_utm_medium',
            'utm_source': 'fake_registration_utm_source',
            'utm_term': 'fake_registration_utm_term'
        }
    }, {
        'username': 'fake-user2',
        'year_of_birth': 1980,
        'full_name': 'fake user2',
        'email': 'fake-user2@fake.email',
        'language': 'fr',
        'country': 'US',
        'goals': 'test-goals',
        'level_of_education': 'a',
        'gender': 'f',
        'registration_date': datetime(2016, 1, 1, 11, 11, 11),
        'courses': [{
            'username': 'fake-user2',
            'list_price': Decimal('4.44'),
            'order_id': 2,
            'unit_price': Decimal('20.22'),
            'coupon_codes': ['fake-code2'],
            'purchase_date': datetime(2017, 1, 1, 11, 11, 11),
            'course_id': 'course-v1:testX:fake-course-id2',
            'quantity': 2
        }],
        'tracking': {
            'utm_campaign': 'test_registration_utm_campaign',
            'utm_content': 'test_registration_utm_content',
            'utm_medium': 'test_registration_utm_medium',
            'utm_source': 'test_registration_utm_source',
            'utm_term': 'test_registration_utm_term'
        }
    }
]
