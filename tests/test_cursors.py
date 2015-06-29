#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test Cursors
------------

Tests for `django-cursor-pagination` cursors module.
"""
from __future__ import absolute_import

from django.utils import six

from cursor_pagination.cursors.signed import SignedBase64Cursor

from .base import CursorBaseTestCase
from .models import ExampleModel


class CursorInterfaceTestMixin(object):
    def test_tokenization(self):
        """
        Tests generating tokens either via direct call or conversion to string.
        """
        queryset = ExampleModel.objects.all()
        value = queryset[self.PAGE_SIZE]
        cursor = self.cursor_class(queryset, border_obj=value)

        token = cursor.token
        str_token = six.text_type(token)
        self.assertEqual(token, str_token)

    def test_untokenization(self):
        """
        Ensures that tokenized cursors return the same cursor.
        """
        queryset = ExampleModel.objects.all()
        value = queryset[self.PAGE_SIZE]
        cursor = self.cursor_class(queryset, border_obj=value)

        token = cursor.token

        cursor2 = self.cursor_class(queryset, token=token)
        self.assertEqual(cursor, cursor2)

        token2 = cursor2.token
        self.assertEqual(token, token2)

    def test_equivalence(self):
        queryset = ExampleModel.objects.all()
        value = queryset[self.PAGE_SIZE]
        cursor = self.cursor_class(queryset, border_obj=value)
        cursor2 = self.cursor_class(queryset, border_obj=value)

        self.assertEqual(cursor, cursor2)

    def test_serialization(self):
        queryset = ExampleModel.objects.all()
        value = queryset[self.PAGE_SIZE]
        cursor = self.cursor_class(queryset, border_obj=value)

        token = cursor.token

        cursor2 = self.cursor_class(queryset, token=token)

        pks = set([x.pk for x in cursor.queryset])
        pks2 = set([x.pk for x in cursor2.queryset])

        self.assertEqual(pks, pks2)


class TestSignedBase64Cursor(CursorInterfaceTestMixin, CursorBaseTestCase):
    cursor_class = SignedBase64Cursor
