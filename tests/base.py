# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.test import TestCase

from .factories import ExampleModelFactory


class CursorBaseTestCase(TestCase):
    NUM_ITEMS = 100
    PAGE_SIZE = 25
    TOO_MANY_PAGES = NUM_ITEMS * 2

    def setUp(self):
        for i in range(self.NUM_ITEMS):
            ExampleModelFactory.create()
