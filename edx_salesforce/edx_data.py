"""Provides functions for retrieving EdX data."""

from __future__ import absolute_import, unicode_literals

from collections import defaultdict

from django.db import connections


QUERIES = {
    'ORDERS_FOR_ORGS': '''
        SELECT
        u.username AS username,
        o.id AS order_id,
        o.date_placed AS purchase_date,
        l.quantity AS quantity,
        l.line_price_before_discounts_incl_tax AS list_price,
        l.line_price_incl_tax AS unit_price,
        p.course_id AS course_id

        FROM order_line AS l
        JOIN order_order AS o
        ON l.order_id = o.id
        JOIN catalogue_product AS p
        ON l.product_id = p.id
        JOIN ecommerce_user AS u
        ON o.user_id = u.id
        WHERE
        p.course_id REGEXP "^course-v1:({orgs}).*$"
    ''',
    'COUPON_CODES_FOR_ORDERS': '''
        SELECT
        o.id AS order_id,
        v.code AS coupon_code

        FROM order_order AS o
        JOIN voucher_voucherapplication AS va
        ON va.order_id = o.id
        JOIN voucher_voucher AS v
        ON v.id = va.voucher_id
        WHERE
        o.id in ({orders})
    ''',
    'LANGUAGE_PREFS_FOR_USERNAMES': '''
        SELECT
        u.username AS username,
        up.value AS language_preference

        FROM auth_user AS u
        JOIN user_api_userpreference AS up
        ON up.user_id = u.id
        WHERE
        up.key = "pref-lang" AND
        u.username in ({usernames})
    ''',
    'USERS_FOR_SITE': '''
        SELECT
        u.username AS username

        FROM auth_user AS u
        JOIN student_userattribute AS ua
        ON ua.user_id = u.id
        WHERE
        ua.name = "created_on_site" AND
        ua.value = "{site_domain}"
    ''',
    'USERS_FOR_USERNAMES': '''
        SELECT
        u.username AS username,
        LOWER(u.email) AS email,
        p.name AS full_name,
        p.country AS country,
        p.year_of_birth AS year_of_birth,
        p.level_of_education AS level_of_education,
        p.goals AS goals,
        p.gender AS gender,
        u.date_joined AS registration_date

        FROM auth_user AS u
        JOIN auth_userprofile AS p
        ON p.user_id = u.id
        WHERE
        u.username in ({usernames})
    ''',
    'TRACKING_DATA_FOR_USERNAMES': '''
        SELECT
        u.username AS username,
        ua.name AS utm_param_name,
        ua.value AS utm_param_value

        FROM auth_user AS u
        JOIN student_userattribute AS ua
        ON ua.user_id = u.id
        WHERE
        ua.name in (
            "registration_utm_campaign",
            "registration_utm_content",
            "registration_utm_medium",
            "registration_utm_source",
            "registration_utm_term"
        ) AND
        u.username in ({usernames})
    ''',
}


def fetch_user_data(site_domain, orgs):
    """
    Return user data associated with the given site and organizations.

    Arguments:
        site_domain (string): The domain of the site which user data will be fetched for.
        orgs (list of strings): The list of organization names which will be used to find
                                course purchases and the associated user data.

    Returns:
        list of dicts, containing the user data.

        Example:
            [{
                'full_name': 'Test User',
                'email': 'test@example.com',
                'country': 'US',
                'year_of_birth': '1977',
                'username': 'TestUser',
                'language': 'en',
                'level_of_education': 'b',
                'goals': 'Learn about foo',
                'gender': 'f',
                'registration_date': datetime.datetime(2016, 2, 14, 0, 0, 0),
                'tracking': {
                    'utm_source': 'test',
                    'utm_medium': 'test',
                    'utm_campaign': 'test',
                    'utm_term': 'test',
                    'utm_content': 'test'
                },
                'courses': [{
                    'coupon_codes': [u'TESTCODE'],
                    'course_id': u'course-v1:TestOrgX+TestCourse+1T2017',
                    'purchase_date': datetime.datetime(2017, 2, 14, 0, 0, 0),
                    'list_price': Decimal('100.00'),
                    'order_id': 10000000L,
                    'quantity': 1L,
                    'unit_price': Decimal('90.00'),
                    'username': u'TestUser'
                }]
            }]
    """
    order_data = _fetch_order_data(orgs)
    site_users = _fetch_users_for_site(site_domain)

    usernames = {item['username'] for item in order_data + site_users}

    user_data = _fetch_user_data(usernames)
    language_pref_data = _fetch_language_preference_data(usernames)
    tracking_data = _fetch_tracking_data(usernames)

    return _munge_user_data(user_data, language_pref_data, tracking_data, order_data)


def _dictfetchall(cursor):
    """
    Return each row from a cursor as a dict.
    """
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def _fetch_coupon_data(order_ids):
    """
    Return any coupon codes associated with the given order IDs.

    Arguments:
        order_ids (list of strings): The order IDs for which to find coupon codes.

    Returns:
        list of dicts, containing the coupon data.

        Example:
            [{
                'order_id': 10000000L,
                'coupon_code': u'TESTCODE'
            }]
    """
    coupon_data = []
    with connections['ecommerce'].cursor() as cursor:
        cursor.execute(QUERIES['COUPON_CODES_FOR_ORDERS'].format(orders=','.join(order_ids)))
        coupon_data = _dictfetchall(cursor)
    return coupon_data


def _fetch_language_preference_data(usernames):
    """
    Return language preference data for the given users.

    Arguments:
        usernames (list of strings): The usernames to fetch language preference data for.

    Returns:
        list of dicts, containing the language preference data.

        Example:
            [{
                'username': 'TestUser',
                'language_preference': 'en'
            },{
                'username': 'TestUser',
                'language_preference': 'ar'
            }]
    """
    language_pref_data = []
    with connections['default'].cursor() as cursor:
        cursor.execute(
            QUERIES['LANGUAGE_PREFS_FOR_USERNAMES'].format(usernames=','.join(['"{}"'.format(u) for u in usernames]))
        )
        language_pref_data = _dictfetchall(cursor)
    return language_pref_data


def _fetch_order_data(orgs):
    """
    Return order data associated with the given organizations.

    An order is associated with an organization if the order contains a product
    that is associated with a course under that organization.

    Arguments:
        orgs (list of strings): The list of organization names which will be used to find order data.

    Returns:
        list of dicts, containing the order data.

        Example:
            [{
                'coupon_codes': [u'TESTCODE'],
                'course_id': u'course-v1:TestOrgX+TestCourse+1T2017',
                'purchase_date': datetime.datetime(2017, 2, 14, 0, 0, 0),
                'list_price': Decimal('100.00'),
                'order_id': 10000000L,
                'quantity': 1L,
                'unit_price': Decimal('90.00'),
                'username': u'TestUser'
            }]
    """
    order_data = []
    with connections['ecommerce'].cursor() as cursor:
        cursor.execute(QUERIES['ORDERS_FOR_ORGS'].format(orgs='|'.join(orgs)))
        order_data = _dictfetchall(cursor)

    order_ids = [str(order['order_id']) for order in order_data]
    coupon_data = _fetch_coupon_data(order_ids)

    return _munge_order_data(order_data, coupon_data)


def _fetch_tracking_data(usernames):
    """
    Return campaign tracking data for the given users.

    Arguments:
        usernames (list of strings): The usernames to fetch tracking data for.

    Returns:
        list of dicts, containing the campaign tracking data.

        Example:
            [{
                'username': 'TestUser',
                'utm_param_name': 'registration_utm_campaign',
                'utm_param_value': 'test'
            },{
                'username': 'TestUser',
                'utm_param_name': 'registration_utm_source',
                'utm_param_value': 'test'
            }]
    """
    tracking_data = []
    with connections['default'].cursor() as cursor:
        cursor.execute(
            QUERIES['TRACKING_DATA_FOR_USERNAMES'].format(usernames=','.join(['"{}"'.format(u) for u in usernames]))
        )
        tracking_data = _dictfetchall(cursor)
    return tracking_data


def _fetch_user_data(usernames):
    """
    Return user data for the given users.

    Arguments:
        usernames (list of strings): The usernames to fetch data for.

    Returns:
        list of dicts, containing the user data.

        Example:
            [{
                'full_name': 'Test User',
                'email': 'test@example.com',
                'country': 'US',
                'year_of_birth': '1977',
                'username': 'TestUser',
                'level_of_education': 'b',
                'goals': 'Learn about foo',
                'gender': 'f',
                'registration_date': datetime.datetime(2016, 2, 14, 0, 0, 0)
            }]
    """
    user_data = []
    with connections['default'].cursor() as cursor:
        cursor.execute(
            QUERIES['USERS_FOR_USERNAMES'].format(usernames=','.join(['"{}"'.format(u) for u in usernames]))
        )
        user_data = _dictfetchall(cursor)
    return user_data


def _fetch_users_for_site(site_domain):
    """
    Return users whose accounts were created on the given site.

    Arguments:
        site_domain (string): The domain of the site to find users for.

    Returns:
        list of dicts, containing the user's usernames.

        Example:
            [{
                'username': u'TestUser'
            }]
    """
    users = []
    with connections['default'].cursor() as cursor:
        cursor.execute(QUERIES['USERS_FOR_SITE'].format(site_domain=site_domain))
        users = _dictfetchall(cursor)
    return users


def _munge_order_data(order_data, coupon_data):
    """
    Return the order data with associated coupon codes added to each order.
    """
    coupons_by_order_id = defaultdict(set)
    for coupon in coupon_data:
        order_id = coupon['order_id']
        coupon_code = coupon['coupon_code']
        coupons_by_order_id[order_id].add(coupon_code)

    for order in order_data:
        order_id = order['order_id']
        order['coupon_codes'] = list(coupons_by_order_id.get(order_id, set()))

    return order_data


def _munge_user_data(user_data, language_pref_data, tracking_data, order_data):
    """
    Return user data with associated course purchase data added to each user.
    """
    orders_by_username = defaultdict(list)
    for order in order_data:
        username = order['username']
        orders_by_username[username].append(order)

    language_prefs_by_username = defaultdict(set)
    for item in language_pref_data:
        username = item['username']
        language_pref = item['language_preference']
        language_prefs_by_username[username].add(language_pref)

    tracking_by_username = defaultdict(dict)
    for item in tracking_data:
        username = item['username']
        utm_param_name = item['utm_param_name'].replace('registration_', '')
        utm_param_value = item['utm_param_value']
        tracking_by_username[username][utm_param_name] = utm_param_value

    for user in user_data:
        username = user['username']
        user['language'] = language_prefs_by_username.get(username, set([None])).pop()
        user['courses'] = orders_by_username.get(username, [])
        user['tracking'] = tracking_by_username.get(username, {})

    return user_data
