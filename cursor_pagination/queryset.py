# -*- coding: utf-8 -*-
from __future__ import absolute_import


from django.db import models

from .cursors import Cursor
# TODO: Make this configurable
from .cursors.signed import SignedBase64Cursor


class CursorQueryset(models.query.QuerySet):
    def cursor(self):
        return SignedBase64Cursor(self)

    def from_cursor(self, cursor):
        if not isinstance(cursor, Cursor):
            cursor = SignedBase64Cursor(self, token=cursor)
        return cursor.queryset
