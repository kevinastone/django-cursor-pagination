# -*- coding: utf-8 -*-
from __future__ import absolute_import


from django.db import models

# TODO: Make this configurable
from .cursors.signed import SignedBase64Cursor as Cursor


class CursorQueryset(models.query.QuerySet):
    def next_cursor(self):
        return Cursor.from_queryset(self, ascending=True)

    def previous_cursor(self):
        return Cursor.from_queryset(self, ascending=False)

    def from_cursor(self, cursor):
        return cursor.queryset(self)
