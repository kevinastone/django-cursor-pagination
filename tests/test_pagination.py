#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Paginator
------------

Tests for `django-cursor-pagination` paginator module.
"""
from __future__ import absolute_import

from django.test import TestCase

from .factories import TestModelFactory
from .models import TestModel

from cursor_pagination.paginator import Paginator


NUM_ITEMS = 200
PAGE_SIZE = 25

TOO_MANY_PAGES = 1000


class TestCursorPagination(TestCase):

    def setUp(self):
        for i in range(NUM_ITEMS):
            TestModelFactory.create()

    def test_pagination(self):
        queryset = TestModel.objects.order_by('pk')
        page_count = 0
        object_count = 0
        paginator = Paginator(queryset, PAGE_SIZE)
        for i in range(TOO_MANY_PAGES):
            page_size = len(paginator)
            if not page_size:
                break
            object_count += page_size
            page_count += 1

            cursor = paginator.next_cursor()
            paginator.from_cursor(cursor)

        self.assertEqual(object_count, NUM_ITEMS)
        self.assertEqual(page_count, NUM_ITEMS / PAGE_SIZE)
