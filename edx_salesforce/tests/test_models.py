#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the `edx-salesforce` models module.
"""

from __future__ import absolute_import, unicode_literals
from django.test import TestCase


class SalesForceTests(TestCase):

    def setUpClass(self):
        print "setting up TestClass"
        pass

    def setUpTestData(self):
        print "setting up TestData"
        pass

    def setUp(self):
        print "setting up TestData"

    def test_first_testcase(self):
        print "hello world"
