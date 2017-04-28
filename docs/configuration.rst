.. _configuration:

Configuration
=============

Before running the sync_salesforce command, you must first configure
the database settings needed to connect to the Open EdX databases and
the Salesforce account you are synchronizing.

Create a private.py settings file under the settings directory:

.. code-block:: python

    DATABASES = {
        'default': {
            'ATOMIC_REQUESTS': True,
            'ENGINE': 'django.db.backends.mysql',
            'NAME': '[edxapp database name]',
            'USER': '[edxapp database user]',
            'PASSWORD': '[edxapp database password]',
            'HOST': '[edxapp database host]',
            'PORT': '3306',
        },
        'ecommerce': {
            'ATOMIC_REQUESTS': True,
            'ENGINE': 'django.db.backends.mysql',
            'NAME': '[ecommerce database name]',
            'USER': '[ecommerce database user]',
            'PASSWORD': '[ecommerce database password]',
            'HOST': '[ecommerce database host]',
            'PORT': '3306',
        },
        'salesforce': {
            'ENGINE': 'salesforce.backend',
            'CONSUMER_KEY': '[Salesforce API consumer key]',
            'CONSUMER_SECRET': '[Salesforce API consumer secret]',
            'USER': '[Salesforce username]',
            'PASSWORD': '[Salesforce password]',
            'HOST': '[https://login.salesforce.com or https://test.salesforce.com]',
        }
    }
