# -*- coding: utf-8 -*-
from __future__ import absolute_import


from django.db import models
from django.db.models.sql.query import Query

# TODO: Make this configurable
from .cursors.signed import SignedBase64Cursor as Cursor


class CursorQueryset(models.query.QuerySet):
    def _get_cursor(self, ascending=True):
        query = self.query
        if not isinstance(query, Query):
            raise Exception(
                "Cannot retrieve cursor unless a Query is available"
            )

        if ascending:
            mark = query.high_mark - query.low_mark - 1
        else:
            mark = 0

        value = self[mark]
        cursor = Cursor.from_queryset(self, value, ascending=ascending)
        return cursor

    def next_cursor(self):
        return self._get_cursor(ascending=True)

    def previous_cursor(self):
        return self._get_cursor(ascending=False)

    def from_cursor(self, cursor):
        qs = self
        for parameter in cursor.parameters:
            qs = qs.filter(**parameter.filter_param)
        return qs
