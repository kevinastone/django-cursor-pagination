# -*- coding: utf-8 -*-
from __future__ import absolute_import

import operator

from django.utils.encoding import python_2_unicode_compatible

from django.db.models import Q
from django.db.models.sql.query import Query


class CursorParameter(object):
    def __init__(self, field_name, value, ascending=True):
        self.field_name = field_name
        self.value = value
        self.ascending = ascending

    @property
    def filter_param(self):
        comparison = "gt" if self.ascending else "lt"

        param = {
            "{field_name}__{comparison}".format(
                field_name=self.field_name,
                comparison=comparison): self.value
        }
        return Q(**param)

    @property
    def eq_param(self):
        return Q(**{
            self.field_name: self.value
        })

    def to_json(self):
        return [self.field_name, self.value, self.ascending]

    @classmethod
    def from_json(cls, data):
        return cls(*data)

    def reverse(self):
        return self.__class__(
            self.field_name,
            self.value,
            not self.ascending,
        )

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "CursorParameter({field_name}, {value}, " \
            "ascending={ascending})".format(
                field_name=repr(self.field_name),
                value=repr(self.value),
                ascending=repr(self.ascending),
            )


@python_2_unicode_compatible
class BaseCursor(object):
    def __init__(self, *parameters):
        self.parameters = parameters

    @classmethod
    def name_to_field(cls, queryset, field_name):
        if field_name[0] == '-':
            # parameter_ascending = not ascending
            field_name = field_name[1:]
        if field_name == 'pk':
            field = queryset.query.get_meta().pk
        else:
            field = queryset.query.get_meta().get_field(field_name)
        return field

    @classmethod
    def get_ordering(cls, queryset):
        ordering = list(queryset.query.extra_order_by) + \
            list(queryset.query.order_by)
        if not ordering and queryset.query.default_ordering:
            ordering = list(queryset.query.get_meta().ordering)
        if not ordering:
            ordering = []

        # Force primary key to be in the ordering to ensure consistent ordering
        pk_field_name = queryset.query.get_meta().pk.name
        if 'pk' not in ordering and pk_field_name not in ordering:
            ordering.append('pk')

        # Iterate and quit when you find the first unique column
        # (the remainder are irrelevant)
        sort_ordering = []
        for field_name in ordering:
            sort_ordering.append(field_name)
            field = cls.name_to_field(queryset, field_name)
            if field.unique:
                break

        return sort_ordering

    @classmethod
    def _get_edge_item(cls, queryset, ascending=True):
        """
        Finds the item closest to the cursor edge for developing the filter
        parameters to build adjacent querysets.
        """

        query = queryset.query
        if not isinstance(query, Query):
            raise Exception(
                "Cannot retrieve cursor unless a Query is available"
            )

        if ascending:
            mark = query.high_mark - query.low_mark - 1
        else:
            mark = 0

        return queryset[mark]

    @classmethod
    def from_queryset(cls, queryset, border_obj=None, ascending=True):
        if not border_obj:
            border_obj = cls._get_edge_item(queryset, ascending)

        ordering = cls.get_ordering(queryset)
        parameters = []
        for field_name in ordering:
            parameter_ascending = ascending

            if field_name[0] == '-':
                parameter_ascending = not ascending
            field = cls.name_to_field(queryset, field_name)

            parameter = CursorParameter(
                field.get_attname(),
                value=getattr(border_obj, field.get_attname()),
                ascending=parameter_ascending,
            )
            parameters.append(parameter)
        return cls(*parameters)

    def queryset(self, queryset):
        params = []
        stacked_params = Q()
        for parameter in self.parameters:
            params.append(parameter.filter_param & stacked_params)
            stacked_params &= parameter.eq_param
        queryset = queryset.filter(reduce(operator.or_, params))
        ordering = self.get_ordering(queryset)
        return queryset.order_by(*ordering)

    def to_token(self):
        raise NotImplementedError(
            "Need to implement `to_token` in a sub-class")

    @classmethod
    def from_token(cls, token):
        raise NotImplementedError(
            "Need to implement `from_token` in a sub-class")

    def reverse(self):
        return self.__class__(*[p.reverse() for p in self.parameters])

    def __str__(self):
        return self.to_token()

    def __repr__(self):
        return "{cls}({parameters})".format(
            cls=self.__class__.__name__,
            parameters=', '.join(repr(x) for x in self.parameters)
        )

    def __eq__(self, other):
        return self.parameters == other.parameters
