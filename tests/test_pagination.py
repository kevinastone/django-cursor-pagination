#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Paginator
--------------

Tests for `django-cursor-pagination` paginator module.
"""
from __future__ import absolute_import

from cursor_pagination.paginator import Paginator

from .base import CursorBaseTestCase
from .models import ExampleModel


class TestCursorPagination(CursorBaseTestCase):
    def test_iteration(self):
        queryset = ExampleModel.objects.all()
        page_count = 0
        object_count = 0
        paginator = Paginator(queryset, self.PAGE_SIZE)
        for cursor in paginator:
            page_size = len(cursor.queryset[:self.PAGE_SIZE])
            object_count += page_size
            page_count += 1

        self.assertEqual(object_count, self.NUM_ITEMS)
        self.assertEqual(page_count, self.NUM_ITEMS / self.PAGE_SIZE)

    def test_construction(self):
        queryset = ExampleModel.objects.all()
        page_count = 0
        object_count = 0
        paginator = Paginator(queryset, self.PAGE_SIZE)
        cursor = next(iter(paginator))
        paginator2 = Paginator(queryset, self.PAGE_SIZE, cursor=cursor)

        for i in range(self.TOO_MANY_PAGES):
            page_size = len(cursor.queryset[:self.PAGE_SIZE])
            object_count += page_size
            page_count += 1

            it = iter(paginator2)

            try:
                next(it)
                cursor = next(it)
            except StopIteration:
                break

            paginator2.update_cursor(cursor)

        self.assertEqual(object_count, self.NUM_ITEMS)
        self.assertEqual(page_count,
                         self.NUM_ITEMS / self.PAGE_SIZE)
