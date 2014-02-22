#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Managers
-------------

Tests for `django-cursor-pagination` managers module.
"""
from __future__ import absolute_import

from .base import CursorBaseTestCase
from .models import TestModel


class TestCursorManagerByPrimaryKey(CursorBaseTestCase):
    def test_ordering_ascending(self):
        qs = TestModel.objects.order_by('pk')
        first_group = qs[:self.PAGE_SIZE]
        cursor = first_group.next_cursor()

        qs2 = qs.from_cursor(cursor)

        second_group = qs2[:self.PAGE_SIZE]

        first_pks = set(x.pk for x in first_group)
        second_pks = set(x.pk for x in second_group)

        self.assertFalse(first_pks & second_pks)
        for count in second_pks:
            self.assertGreater(
                count, max(first_pks),
                "Cursor didn't maintain ordering"
            )

    def test_ordering_descending(self):
        qs = TestModel.objects.order_by('-pk')
        first_group = qs[:self.PAGE_SIZE]
        cursor = first_group.next_cursor()

        qs2 = qs.from_cursor(cursor)

        second_group = qs2[:self.PAGE_SIZE]

        first_pks = set(x.pk for x in first_group)
        second_pks = set(x.pk for x in second_group)

        self.assertFalse(first_pks & second_pks)
        for count in second_pks:
            self.assertLess(
                count, min(first_pks),
                "Cursor didn't maintain ordering"
            )


class TestCursorManagerByInteger(CursorBaseTestCase):
    def test_ordering_ascending(self):
        qs = TestModel.objects.order_by('count_field')
        first_group = qs[:self.PAGE_SIZE]
        cursor = first_group.next_cursor()

        qs2 = qs.from_cursor(cursor)

        second_group = qs2[:self.PAGE_SIZE]

        first_counts = set(x.count_field for x in first_group)
        second_counts = set(x.count_field for x in second_group)

        for count in second_counts:
            self.assertGreaterEqual(
                count, max(first_counts),
                "Cursor didn't maintain ordering"
            )

    def test_ordering_descending(self):
        qs = TestModel.objects.order_by('-count_field')
        first_group = qs[:self.PAGE_SIZE]
        cursor = first_group.next_cursor()

        qs2 = qs.from_cursor(cursor)

        second_group = qs2[:self.PAGE_SIZE]

        first_counts = set(x.count_field for x in first_group)
        second_counts = set(x.count_field for x in second_group)

        for count in second_counts:
            self.assertLessEqual(
                count, min(first_counts),
                "Cursor didn't maintain ordering"
            )
