# -*- coding: utf-8 -*-
from __future__ import absolute_import


from model_utils.managers import PassThroughManager

from .queryset import CursorQueryset


class CursorManager(PassThroughManager):
	def __init__(self):
		super(CursorManager, self).__init__(CursorQueryset)

