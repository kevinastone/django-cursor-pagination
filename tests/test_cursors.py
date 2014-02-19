#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Cursors
------------

Tests for `django-cursor-pagination` cursors module.
"""
from __future__ import absolute_import

from cursor_pagination.cursors.signed import SignedBase64Cursor as Cursor

from .base import CursorBaseTestCase
from .models import TestModel


class TestCursors(CursorBaseTestCase):
    def test_tokenization(self):
        original_queryset = TestModel.objects.order_by('pk')
        value = original_queryset[self.PAGE_SIZE]
        cursor = Cursor.from_queryset(original_queryset, value)

        token = cursor.to_token()

        cursor2 = Cursor.from_token(token)
        self.assertEqual(cursor, cursor2)

        token2 = cursor2.to_token()
        self.assertEqual(token, token2)

    def test_equivalence(self):
        original_queryset = TestModel.objects.order_by('pk')
        value = original_queryset[self.PAGE_SIZE]
        cursor = Cursor.from_queryset(original_queryset, value)
        cursor2 = Cursor.from_queryset(original_queryset, value)

        self.assertEqual(cursor, cursor2)

    def test_serialization(self):
        original_queryset = TestModel.objects.order_by('pk')
        value = original_queryset[self.PAGE_SIZE]
        cursor = Cursor.from_queryset(original_queryset, value)

        token = cursor.to_token()

        cursor2 = Cursor.from_token(token)

        qs = original_queryset.from_cursor(cursor)
        qs2 = original_queryset.from_cursor(cursor2)

        pks = set([x.pk for x in qs])
        pks2 = set([x.pk for x in qs2])

        self.assertEqual(pks, pks2)
