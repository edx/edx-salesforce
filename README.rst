edx-salesforce
==============

.. image:: https://img.shields.io/pypi/v/edx-salesforce.svg
    :target: https://pypi.python.org/pypi/edx-salesforce/
    :alt: PyPI

.. image:: https://travis-ci.org/edx/edx-salesforce.svg?branch=master
    :target: https://travis-ci.org/edx/edx-salesforce
    :alt: Travis

.. image:: http://codecov.io/github/edx/edx-salesforce/coverage.svg?branch=master
    :target: http://codecov.io/github/edx/edx-salesforce?branch=master
    :alt: Codecov

.. image:: https://readthedocs.org/projects/edx-salesforce/badge/?version=latest
    :target: http://edx-salesforce.readthedocs.io/en/latest/
    :alt: Documentation

.. image:: https://img.shields.io/pypi/pyversions/edx-salesforce.svg
    :target: https://pypi.python.org/pypi/edx-salesforce/
    :alt: Supported Python versions

.. image:: https://img.shields.io/github/license/edx/edx-salesforce.svg
    :target: https://github.com/edx/edx-salesforce/blob/master/LICENSE.txt
    :alt: License

Django application used to integrate Open EdX with Salesforce.

Overview
--------

This Django application uses the django-salesforce_ package to provide a
Django ORM for communicating with the Salesforce API to CRUD Salesforce
objects.

The application provides the sync_salesforce Django command which will
query the databases that store Open EdX data related to user profiles
and course purchases and then create or update objects in Salesforce.

.. _django-salesforce: https://github.com/django-salesforce/django-salesforce

Documentation
-------------

The full documentation is at https://edx-salesforce.readthedocs.org.

License
-------

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see ``LICENSE.txt`` for details.

How To Contribute
-----------------

Contributions are very welcome.

Please read `How To Contribute <https://github.com/edx/edx-platform/blob/master/CONTRIBUTING.rst>`_ for details.

Even though they were written with ``edx-platform`` in mind, the guidelines
should be followed for Open edX code in general.

PR description template can be found at
`PR_TEMPLATE.md <https://github.com/edx/edx-salesforce/blob/master/PR_TEMPLATE.md>`_

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@edx.org.

Getting Help
------------

Have a question about this repository, or about Open edX in general?  Please
refer to this `list of resources`_ if you need any assistance.

.. _list of resources: https://open.edx.org/getting-help
