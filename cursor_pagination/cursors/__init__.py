# -*- coding: utf-8 -*-
from __future__ import absolute_import


class CursorParameter(object):
    def __init__(self, field_name, value, ascending=True, unique=False):
        self.field_name = field_name
        self.value = value
        self.ascending = ascending
        self.unique = unique

    @property
    def filter_param(self):
        operator = "gt" if self.ascending else "lt"

        if not self.unique:
            # If the field is not unique, we have to permit equivalent values
            operator = operator + "e"

        param = {
            "{field_name}__{operator}".format(
                field_name=self.field_name,
                operator=operator): self.value
        }
        return param

    def to_json(self):
        return [self.field_name, self.value, self.ascending, self.unique]

    @classmethod
    def from_json(cls, data):
        return cls(*data)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "CursorParameter({field_name}, {value}, " \
            "ascending={ascending}, unique={unique})".format(
                field_name=repr(self.field_name),
                value=repr(self.value),
                ascending=repr(self.ascending),
                unique=repr(self.unique)
            )


class BaseCursor(object):
    def __init__(self, *parameters):
        self.parameters = parameters

    @staticmethod
    def get_ordering(queryset):
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

        return ordering

    @classmethod
    def from_queryset(cls, queryset, obj, ascending=True):
        ordering = cls.get_ordering(queryset)
        parameters = []
        for field_name in ordering:
            parameter_ascending = ascending

            if field_name[0] == '-':
                parameter_ascending = not ascending
                field_name = field_name[1:]

            if field_name == 'pk':
                field = queryset.query.get_meta().pk
            else:
                field = queryset.query.get_meta().get_field(field_name)

            parameter = CursorParameter(
                field_name,
                value=getattr(obj, field_name),
                ascending=parameter_ascending, unique=field.unique
            )
            parameters.append(parameter)
        return cls(*parameters)

    def __repr__(self):
        return "{cls}({pk}, {parameters})".format(
            cls=self.__class__.__name__,
            parameters=', '.join(repr(x) for x in self.parameters)
        )

    def __eq__(self, other):
        return self.parameters == other.parameters
