#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Managers
------------

Tests for `django-cursor-pagination` managers module.
"""
from __future__ import absolute_import

from django.test import TestCase

from .factories import TestModelFactory
from .models import TestModel


NUM_ITEMS = 200
PAGE_SIZE = 25


class TestCursorManagerByPrimaryKey(TestCase):

    def setUp(self):
        for i in range(NUM_ITEMS):
            TestModelFactory.create()

    def test_ordering_next_ascending(self):
        qs = TestModel.objects.order_by('pk')
        first_group = qs[:PAGE_SIZE]
        cursor = first_group.next_cursor()

        qs2 = qs.from_cursor(cursor)

        second_group = qs2[:PAGE_SIZE]

        first_pks = set(x.pk for x in first_group)
        second_pks = set(x.pk for x in second_group)

        self.assertFalse(first_pks & second_pks)
        for count in second_pks:
            self.assertGreater(
                count, max(first_pks),
                "Cursor didn't maintain ordering"
            )

    def test_ordering_previous_ascending(self):
        qs = TestModel.objects.order_by('pk')
        first_group = qs[PAGE_SIZE:2*PAGE_SIZE]
        cursor = first_group.previous_cursor()

        qs2 = qs.from_cursor(cursor)

        second_group = qs2[:PAGE_SIZE]

        first_pks = set(x.pk for x in first_group)
        second_pks = set(x.pk for x in second_group)

        self.assertFalse(first_pks & second_pks)
        for count in second_pks:
            self.assertLess(
                count, min(first_pks),
                "Cursor didn't maintain ordering"
            )

    def test_ordering_next_descending(self):
        qs = TestModel.objects.order_by('-pk')
        first_group = qs[:PAGE_SIZE]
        cursor = first_group.next_cursor()

        qs2 = qs.from_cursor(cursor)

        second_group = qs2[:PAGE_SIZE]

        first_pks = set(x.pk for x in first_group)
        second_pks = set(x.pk for x in second_group)

        self.assertFalse(first_pks & second_pks)
        for count in second_pks:
            self.assertLess(
                count, min(first_pks),
                "Cursor didn't maintain ordering"
            )

    def test_ordering_previous_descending(self):
        qs = TestModel.objects.order_by('-pk')
        first_group = qs[PAGE_SIZE:2*PAGE_SIZE]
        cursor = first_group.previous_cursor()

        qs2 = qs.from_cursor(cursor)

        second_group = qs2[:PAGE_SIZE]

        first_pks = set(x.pk for x in first_group)
        second_pks = set(x.pk for x in second_group)

        self.assertFalse(first_pks & second_pks)
        for count in second_pks:
            self.assertGreater(
                count, max(first_pks),
                "Cursor didn't maintain ordering"
            )


class TestCursorManagerByInteger(TestCase):

    def setUp(self):
        for i in range(NUM_ITEMS):
            TestModelFactory.create()

    def test_ordering_next_ascending(self):
        qs = TestModel.objects.order_by('count_field')
        first_group = qs[:PAGE_SIZE]
        cursor = first_group.next_cursor()

        qs2 = qs.from_cursor(cursor)

        second_group = qs2[:PAGE_SIZE]

        first_counts = set(x.count_field for x in first_group)
        second_counts = set(x.count_field for x in second_group)

        for count in second_counts:
            self.assertGreaterEqual(
                count, max(first_counts),
                "Cursor didn't maintain ordering"
            )

    def test_ordering_previous_ascending(self):
        qs = TestModel.objects.order_by('count_field')
        first_group = qs[PAGE_SIZE:2*PAGE_SIZE]
        cursor = first_group.previous_cursor()

        qs2 = qs.from_cursor(cursor)

        second_group = qs2[:PAGE_SIZE]

        first_counts = set(x.count_field for x in first_group)
        second_counts = set(x.count_field for x in second_group)

        for count in second_counts:
            self.assertLessEqual(
                count, min(first_counts),
                "Cursor didn't maintain ordering"
            )

    def test_ordering_next_descending(self):
        qs = TestModel.objects.order_by('-count_field')
        first_group = qs[:PAGE_SIZE]
        cursor = first_group.next_cursor()

        qs2 = qs.from_cursor(cursor)

        second_group = qs2[:PAGE_SIZE]

        first_counts = set(x.count_field for x in first_group)
        second_counts = set(x.count_field for x in second_group)

        for count in second_counts:
            self.assertLessEqual(
                count, min(first_counts),
                "Cursor didn't maintain ordering"
            )

    def test_ordering_previous_descending(self):
        qs = TestModel.objects.order_by('-count_field')
        first_group = qs[PAGE_SIZE:2*PAGE_SIZE]
        cursor = first_group.previous_cursor()

        qs2 = qs.from_cursor(cursor)

        second_group = qs2[:PAGE_SIZE]

        first_counts = set(x.count_field for x in first_group)
        second_counts = set(x.count_field for x in second_group)

        for count in second_counts:
            self.assertGreaterEqual(
                count, max(first_counts),
                "Cursor didn't maintain ordering"
            )
