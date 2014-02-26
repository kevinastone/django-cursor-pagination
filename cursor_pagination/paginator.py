# -*- coding: utf-8 -*-
"""
Helper class to segment a queryset into Pages with cursors providing consitent
reference points.
"""
from __future__ import absolute_import
from __future__ import division

from django.db.models.query import EmptyQuerySet

from .cursors import Cursor
from .cursors.signed import SignedBase64Cursor


class Page(object):
    def __init__(self, cursor, per_page):
        self.cursor = cursor
        self.per_page = per_page

    def __next__(self):
        current_cursor = self.cursor
        if isinstance(current_cursor.queryset, EmptyQuerySet):
            raise StopIteration

        self.cursor = self.cursor.__class__(
            self.cursor.queryset[self.per_page:])
        return current_cursor

    def next(self):
        return self.__next__()


class Paginator(object):
    def __init__(self, object_list, per_page, cursor=None):
        self.per_page = int(per_page)
        self.object_list = object_list

        self.update_cursor(cursor)

    def update_cursor(self, cursor):
        cursor_class = SignedBase64Cursor
        token = cursor
        if isinstance(cursor, Cursor):
            cursor_class = cursor.__class__
            token = cursor.token
        self.cursor = cursor_class(self.object_list, token=token)

    def __len__(self):
        return len(self.object_list) // self.per_page

    def __iter__(self):
        return Page(self.cursor, self.per_page)
