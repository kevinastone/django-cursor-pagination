# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.utils import six

from .queryset import CursorQueryset


class Paginator(object):
    def __init__(self, object_list, per_page, cursor=None):
        self.per_page = int(per_page)
        self.pristine_object_list = object_list
        if cursor:
            object_list = cursor.queryset(object_list)
        self.object_list = object_list[0:self.per_page]

    def __iter__(self):
        return iter(self.object_list)

    def __len__(self):
        return len(self.object_list)

    def __getitem__(self, index):
        if not isinstance(index, (slice,) + six.integer_types):
            raise TypeError
        return self.object_list[index]

    def from_cursor(self, cursor):
        assert isinstance(self.pristine_object_list, CursorQueryset)
        self.object_list = \
            cursor.queryset(self.pristine_object_list)[0:self.per_page]

    def next_cursor(self):
        assert isinstance(self.object_list, CursorQueryset)
        return self.object_list.next_cursor()
