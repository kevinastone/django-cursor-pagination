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
from .factories import TestModelFactory


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

    def test_queryset_consistent_with_data_insert(self):
        """
        Ensures that a cursor returned from a queryset stays fixed when new
        items are inserted.
        """
        queryset = CursorQueryset(model=TestModel).order_by('count_field')
        cursor = queryset[:self.PAGE_SIZE].next_cursor()

        expected = set([
            x.pk for x in queryset[self.PAGE_SIZE:2*self.PAGE_SIZE]
        ])

        last = queryset[:self.PAGE_SIZE][self.PAGE_SIZE - 1]

        # Now add some instances that would change the indexing
        for i in range(10):
            TestModelFactory.create(count_field=last.count_field - 1)

        queryset2 = queryset.from_cursor(cursor)

        actual = set([x.pk for x in queryset2[:self.PAGE_SIZE]])
        
        self.assertSetEqual(expected, actual)
