# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.db.models import Manager

# Need to substitute model_utils in Django<1.7
try:
    Manager.from_queryset
except AttributeError:
    from model_utils.managers import PassThroughManager as Manager
    Manager.from_queryset = Manager.for_queryset_class

from .queryset import CursorQueryset


CursorManager = Manager.from_queryset(CursorQueryset)
