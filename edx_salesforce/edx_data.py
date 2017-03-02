from collections import defaultdict

from django.db import connections


QUERIES = {
    'ORDERS_FOR_ORGS': '''
        SELECT
        u.username AS username,
        o.id AS order_id,
        o.date_placed AS purchase_date,
        l.line_price_incl_tax AS amount_paid,
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

    ''',
    'TRACKING_DATA_FOR_USERNAMES': '''

    ''',
}


def fetch_user_data(site_domain, orgs):
    """
    Returns user data associated with the given site and organizations.

    Arguments:
        site_domain (string): The domain of the site which user data will be fetched for.
        orgs (list of strings): The list of organization names which will be used to find
                                course purchases and the associated user data.

    Returns:
        list of dicts, containing the user data.

        Example:
            [{
                first_name: 'Test',
                last_name: 'User',
                email: 'test@example.com',
                country: 'MA',
                year_of_birth: '1977',
                username: 'TestUser',
                language: 'en',
                tracking: {
                    utm_source: 'test',
                    utm_medium: 'test',
                    utm_campaign: 'test',
                    utm_term: 'test',
                    utm_content: 'test'
                },
                courses: [{
                    'amount_paid': Decimal('100.00'),
                    'coupon_codes': [u'TESTCODE'],
                    'course_id': u'course-v1:TestOrgX+TestCourse+1T2017',
                    'date_placed': datetime.datetime(2017, 2, 14, 0, 0, 0),
                    'order_id': 10000000L,
                    'username': u'TestUser'
                }]
            }]
    """
    order_data = _fetch_order_data(orgs)
    site_users = _fetch_users_for_site(site_domain)

    usernames = {item['username'] for item in (order_data + site_users)}

    user_data = _fetch_user_data(usernames)
    tracking_data = _fetch_tracking_data(usernames)

    return _munge_user_data(user_data, tracking_data, order_data)


def _dictfetchall(cursor):
    """
    Return each row from a cursor as a dict
    """
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def _fetch_coupon_data(order_ids):
    """
    Returns any coupon codes associated with the given order IDs.

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


def _fetch_order_data(orgs):
    """
    Returns order data associated with the given organizations. An order is associated
    with an organization if the order contains a product that is associated with a
    course under that organization.

    Arguments:
        orgs (list of strings): The list of organization names which will be used to find order data.

    Returns:
        list of dicts, containing the order data.

        Example:
            [{
                'amount_paid': Decimal('100.00'),
                'coupon_codes': [],
                'course_id': u'course-v1:TestOrgX+TestCourse+1T2017',
                'date_placed': datetime.datetime(2017, 2, 14, 0, 0, 0),
                'order_id': 10000000L,
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
    Returns campaign tracking data for the given users.

    Arguments:
        usernames (list of strings): The usernames to fetch tracking data for.

    Returns:
        list of dicts, containing the campaign tracking data.

        Example:
            [{
                username: 'TestUser',
                utm_source: 'test',
                utm_medium: 'test',
                utm_campaign: 'test',
                utm_term: 'test',
                utm_content: 'test'
            }]
    """
    tracking_data = []
    with connections['default'].cursor() as cursor:
        cursor.execute(QUERIES['TRACKING_DATA_FOR_USERNAMES'].format(usernames=usernames))
        tracking_data = _dictfetchall(cursor)
    return tracking_data


def _fetch_user_data(usernames):
    """
    Returns user data for the given users.

    Arguments:
        usernames (list of strings): The usernames to fetch data for.

    Returns:
        list of dicts, containing the user data.

        Example:
            [{
                first_name: 'Test',
                last_name: 'User',
                email: 'test@example.com',
                country: 'MA',
                year_of_birth: '1977',
                username: 'TestUser',
                language: 'en',
            }]
    """
    user_data = []
    with connections['default'].cursor() as cursor:
        cursor.execute(QUERIES['USERS_FOR_USERNAMES'].format(usernames=usernames))
        user_data = _dictfetchall(cursor)
    return user_data


def _fetch_users_for_site(site_domain):
    """
    Returns users whose accounts were created on the given site.

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
    Returns the order data with associated coupon codes added to each order.
    """
    coupons_by_order_id = defaultdict(set)
    for coupon in coupon_data:
        order_id = coupon['order_id']
        coupon_code = coupon['coupon_code']
        coupons_by_order_id[order_id].add(coupon_code)

    for order in order_data:
        order_id = order['order_id']
        order['coupon_codes'] = coupons_by_order_id.get(order_id, [])

    return order_data


def _munge_user_data(user_data, tracking_data, order_data):
    """
    Returns user data with associated course purchase data added to each user.
    """
    orders_by_username = defaultdict(list)
    for order in order_data:
        username = order['username']
        orders_by_username[username].append(order)

    for user in user_data:
        username = user['username']
        user['courses'] = orders_by_username.get(username, [])

    return user_data
