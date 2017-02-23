"""
The module contains a data structure used to create
the edxapp and ecommerce database schemas required for testing.
"""

from __future__ import absolute_import, unicode_literals


SCHEMA = {
    'default': {
        'auth_userprofile': (
            'id int(11) NOT NULL PRIMARY KEY',
            'name varchar(255) NOT NULL',
            'language varchar(255) NOT NULL',
            'year_of_birth int(11) DEFAULT NULL',
            'country varchar(2) DEFAULT NULL',
            'goals varchar(3000) DEFAULT NULL',
            'level_of_education varchar(6) DEFAULT NULL',
            'gender varchar(6) DEFAULT NULL',
            'user_id int(11) NOT NULL',
        ),
        'student_userattribute': (
            'id int(11) NOT NULL PRIMARY KEY',
            'name varchar(255) NOT NULL',
            'value varchar(255) NOT NULL',
            'user_id int(11) NOT NULL',
        ),
        'user_api_userpreference': (
            'id int(11) NOT NULL  PRIMARY KEY',
            '`key` varchar(255) NOT NULL',
            'value varchar(255) NOT NULL',
            'user_id int(11) NOT NULL',
        ),
    },
    'ecommerce': {
        'catalogue_product': (
            'id int(11) NOT NULL PRIMARY KEY',
            'course_id varchar(255)',
        ),
        'ecommerce_user': (
            'id int(11) NOT NULL PRIMARY KEY',
            'username varchar(30) NOT NULL',
        ),
        'order_line': (
            'id int(11) NOT NULL PRIMARY KEY',
            'quantity int(10) NOT NULL',
            'line_price_before_discounts_incl_tax decimal(12,2) NOT NULL',
            'line_price_incl_tax decimal(12,2) NOT NULL',
            'order_id int(11) NOT NULL',
            'product_id int(11)',
        ),
        'order_order': (
            'id int(11) NOT NULL PRIMARY KEY',
            'number varchar(128) NOT NULL',
            'date_placed datetime(6) NOT NULL',
            'user_id int(11) NOT NULL',
        ),
        'voucher_voucher': (
            'id int(11) NOT NULL PRIMARY KEY',
            'code varchar(128) NOT NULL',
        ),
        'voucher_voucherapplication': (
            'id int(11) NOT NULL  PRIMARY KEY',
            'order_id int(11) NOT NULL',
            'voucher_id int(11) NOT NULL',
        ),
    }
}
