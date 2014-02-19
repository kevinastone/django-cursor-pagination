#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Cursors
------------

Tests for `django-cursor-pagination` cursors module.
"""
from __future__ import absolute_import

from django.test import TestCase

from .factories import TestModelFactory
from .models import TestModel

from cursor_pagination.cursors.signed import SignedBase64Cursor as Cursor


NUM_ITEMS = 200
PAGE_SIZE = 25


class TestCursors(TestCase):

    def setUp(self):
        for i in range(NUM_ITEMS):
            TestModelFactory.create()

    def test_tokenization(self):
        original_queryset = TestModel.objects.order_by('pk')
        value = original_queryset[PAGE_SIZE]
        cursor = Cursor.from_queryset(original_queryset, value)

        token = cursor.to_token()

        cursor2 = Cursor.from_token(token)
        self.assertEqual(cursor, cursor2)

        token2 = cursor2.to_token()
        self.assertEqual(token, token2)

    def test_equivalence(self):
        original_queryset = TestModel.objects.order_by('pk')
        value = original_queryset[PAGE_SIZE]
        cursor = Cursor.from_queryset(original_queryset, value)
        cursor2 = Cursor.from_queryset(original_queryset, value)

        self.assertEqual(cursor, cursor2)

    def test_serialization(self):
        original_queryset = TestModel.objects.order_by('pk')
        value = original_queryset[PAGE_SIZE]
        cursor = Cursor.from_queryset(original_queryset, value)

        token = cursor.to_token()

        cursor2 = Cursor.from_token(token)

        qs = original_queryset.from_cursor(cursor)
        qs2 = original_queryset.from_cursor(cursor2)

        pks = set([x.pk for x in qs])
        pks2 = set([x.pk for x in qs2])

        self.assertEqual(pks, pks2)
