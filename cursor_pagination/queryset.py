# -*- coding: utf-8 -*-
from __future__ import absolute_import


from django.db import models

# TODO: Make this configurable
from .cursors import BaseCursor
from .cursors.signed import SignedBase64Cursor as Cursor


class CursorQueryset(models.query.QuerySet):
    def next_cursor(self):
        return Cursor.from_queryset(self, ascending=True)

    def from_cursor(self, cursor):
        if not isinstance(cursor, BaseCursor):
            cursor = Cursor.from_token(cursor)
        return cursor.queryset(self)
