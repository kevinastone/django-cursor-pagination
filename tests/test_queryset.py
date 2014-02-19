#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Queryset
-------------

Tests for `django-cursor-pagination` queryset module.
"""
from __future__ import absolute_import

from cursor_pagination.queryset import CursorQueryset

from .base import CursorBaseTestCase

from .models import TestModel


class TestCursorPagination(CursorBaseTestCase):
    def test_queryset_where_clauses(self):
        queryset = CursorQueryset(model=TestModel).order_by('pk')

        cursor1 = queryset[:self.PAGE_SIZE].next_cursor()
        queryset1 = queryset.from_cursor(cursor1)

        cursor2 = queryset1[:self.PAGE_SIZE].next_cursor()
        queryset2 = queryset.from_cursor(cursor2)

        self.assertEqual(
            len(queryset1.query.where.children),
            len(queryset2.query.where.children), 
            "Cursor generated querysets had different where clause lengths"
        )
