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
        queryset = CursorQueryset(model=TestModel).all()

        cursor1 = queryset[:self.PAGE_SIZE].next_cursor()
        queryset1 = queryset.from_cursor(cursor1)

        cursor2 = queryset1[:self.PAGE_SIZE].next_cursor()
        queryset2 = queryset.from_cursor(cursor2)

        self.assertEqual(
            len(queryset1.query.where.children),
            len(queryset2.query.where.children),
            "Cursor generated querysets had different where clause lengths"
        )

    def test_queryset_uses_cache(self):
        queryset = CursorQueryset(model=TestModel).all()

        # Generate the queryset once to build the cursor
        with self.assertNumQueries(1):
            queryset[:self.PAGE_SIZE].next_cursor()

        # But if we first consume the queryset, the cursor should use the cache
        with self.assertNumQueries(1):
            qs = queryset[:self.PAGE_SIZE]
            # Iterating over the qs should be one db call
            for x in qs:
                pass
            # But should also prime the cache for the cursor generation
            qs.next_cursor()
