#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Cursors
------------

Tests for `django-cursor-pagination` cursors module.
"""
from __future__ import absolute_import

from django.utils import six

from cursor_pagination.cursors import CursorParameter
from cursor_pagination.cursors.signed import SignedBase64Cursor

from .base import CursorBaseTestCase
from .models import TestModel


class CursorInterfaceTestMixin(object):
    def test_tokenization(self):
        """
        Tests generating tokens either via direct call or conversion to string.
        """
        original_queryset = TestModel.objects.all()
        value = original_queryset[self.PAGE_SIZE]
        cursor = self.cursor_class.from_queryset(original_queryset, value)

        token = cursor.to_token()
        str_token = six.text_type(token)
        self.assertEqual(token, str_token)

    def test_untokenization(self):
        """
        Ensures that tokenized cursors return the same cursor.
        """
        original_queryset = TestModel.objects.all()
        value = original_queryset[self.PAGE_SIZE]
        cursor = self.cursor_class.from_queryset(original_queryset, value)

        token = cursor.to_token()

        cursor2 = self.cursor_class.from_token(token)
        self.assertEqual(cursor, cursor2)

        token2 = cursor2.to_token()
        self.assertEqual(token, token2)

    def test_equivalence(self):
        original_queryset = TestModel.objects.all()
        value = original_queryset[self.PAGE_SIZE]
        cursor = self.cursor_class.from_queryset(original_queryset, value)
        cursor2 = self.cursor_class.from_queryset(original_queryset, value)

        self.assertEqual(cursor, cursor2)

    def test_repr_constructor_syntax(self):
        """
        Ensures that the :func:`repr` creates a valid constructor.
        """        
        original_queryset = TestModel.objects.all()
        value = original_queryset[self.PAGE_SIZE]
        cursor = self.cursor_class.from_queryset(original_queryset, value)

        cursor2 = eval(repr(cursor), {
            'CursorParameter': CursorParameter,
            self.cursor_class.__name__: self.cursor_class,
        })

        self.assertEqual(cursor, cursor2)


    def test_serialization(self):
        original_queryset = TestModel.objects.all()
        value = original_queryset[self.PAGE_SIZE]
        cursor = self.cursor_class.from_queryset(original_queryset, value)

        token = cursor.to_token()

        cursor2 = self.cursor_class.from_token(token)

        qs = cursor.queryset(original_queryset)
        qs2 = cursor2.queryset(original_queryset)

        pks = set([x.pk for x in qs])
        pks2 = set([x.pk for x in qs2])

        self.assertEqual(pks, pks2)


class TestSignedBase64Cursor(CursorInterfaceTestMixin, CursorBaseTestCase):
    cursor_class = SignedBase64Cursor
