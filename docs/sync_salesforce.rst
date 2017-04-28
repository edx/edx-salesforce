Synchronizing Open EdX Data with Salesforce
===========================================

If you have not already done so, create/activate a `virtualenv`_,
install requirements as described in :ref:`getting_started`, and
configure database settings as described in
:ref:`configuration`. Unless otherwise stated, assume all
terminal code below is executed within the virtualenv.

.. _virtualenv: https://virtualenvwrapper.readthedocs.org/en/latest/


Run the sync_salesforce command
-------------------------------

The sync_salesforce command requires the following options:

.. list-table::
   :widths: 25 60 20
   :header-rows: 1

   * - Option
     - Description
     - Example
   * - ``-s, --site-domain``
     - The domain of the site used to select Open EdX
       user data for synchronization.
     - foo.example.com
   * - ``-o, --orgs``
     - A comma-separated list of organization names used
       to select course purchase data for synchronization.
     - FooX,BarX

To run the command:

.. code-block:: bash

    $ python manage.py sync_salesforce -s [site domain] -o [organization] --settings=settings.local

Limitations
-----------

The sync_salesforce command currently expects a number of custom
fields to be defined on the Lead and Contact objects in Salesforce.
Please see the `source code`_ for details.

.. _`source code`: https://github.com/edx/edx-salesforce
