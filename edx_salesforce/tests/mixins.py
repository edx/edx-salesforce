"""
Mixin to create test edxapp and ecommerce database schemas and load test data into them.
"""

from __future__ import absolute_import, unicode_literals

from django.db import connections

from edx_salesforce.tests.fixtures.data import DATA
from edx_salesforce.tests.fixtures.schema import SCHEMA


class DatabaseMixin(object):
    """
    Mixin for creating the test database schema and loading test data.
    """

    @classmethod
    def setUpTestData(cls):  # pylint: disable=invalid-name
        """
        Set up the sample data.
        """
        for database in ('default', 'ecommerce'):
            with connections[database].cursor() as cursor:
                cls._create_schema(cursor, SCHEMA[database])
                cls._load_data(cursor, DATA[database])

    @classmethod
    def _create_schema(cls, cursor, schema):
        """
        Creates test database schema.
        """
        for table, columns in schema.items():
            cursor.execute('CREATE TABLE {table} ({columns})'.format(table=table, columns=','.join(columns)))

    @classmethod
    def _load_data(cls, cursor, data):
        """
        Loads test data.
        """
        for table, insert_data in data.items():
            columns = insert_data['columns']
            for values in insert_data['records']:
                cursor.execute(
                    'INSERT INTO {table} ({columns}) VALUES ({values})'.format(
                        table=table,
                        columns=','.join(columns),
                        values=','.join(str(v) for v in values)
                    )
                )
