# -*- coding: utf-8 -*-
from __future__ import absolute_import

import operator

from django.utils.six.moves import reduce
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import lazy_property

from django.db.models import Q
from django.db.models.sql.query import Query

from ..query import reduce_redundant_clauses


class MissingBorderObjectException(Exception):
    pass


class CursorParameter(object):
    def __init__(self, field_name, value, ascending=True, inclusive=True):
        self.field_name = field_name
        self.value = value
        self.ascending = ascending
        self.inclusive = inclusive

    @property
    def filter_param(self):
        comparison = "gt" if self.ascending else "lt"

        if self.inclusive:
            comparison += "e"

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
        return [self.field_name, self.value, self.ascending, self.inclusive]

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
            "ascending={ascending}, inclusive={inclusive})".format(
                field_name=repr(self.field_name),
                value=repr(self.value),
                ascending=repr(self.ascending),
                inclusive=repr(self.inclusive),
            )


@python_2_unicode_compatible
class Cursor(object):
    def __init__(self, queryset, border_obj=None, inclusive=True,
                 ascending=True, token=None):
        self._queryset = queryset
        self.border_obj = border_obj
        self.inclusive = inclusive
        self.ascending = ascending
        self._parameters = None
        if token:
            self.token = token

    def _name_to_field(self, field_name):
        if field_name[0] == '-':
            # parameter_ascending = not ascending
            field_name = field_name[1:]
        if field_name == 'pk':
            field = self._queryset.query.get_meta().pk
        else:
            field = self._queryset.query.get_meta().get_field(field_name)
        return field

    def get_ordering(self):
        ordering = list(self._queryset.query.extra_order_by) + \
            list(self._queryset.query.order_by)
        if not ordering and self._queryset.query.default_ordering:
            ordering = list(self._queryset.query.get_meta().ordering)
        if not ordering:
            ordering = []

        # Force primary key to be in the ordering to ensure consistent ordering
        pk_field_name = self._queryset.query.get_meta().pk.name
        if 'pk' not in ordering and pk_field_name not in ordering:
            ordering.append('pk')

        # Iterate and quit when you find the first unique column
        # (the remainder are irrelevant)
        sort_ordering = []
        for field_name in ordering:
            sort_ordering.append(field_name)
            field = self._name_to_field(field_name)
            if field.unique:
                break
        return sort_ordering

    def _get_edge_item(self):
        """
        Finds the item closest to the cursor edge for developing the filter
        parameters to build adjacent querysets.
        """

        query = self._queryset.query
        if not isinstance(query, Query):
            raise Exception(
                "Cannot retrieve cursor unless a Query is available"
            )

        if self.ascending:
            mark = 0
        else:
            mark = query.high_mark - query.low_mark - 1
        try:
            return self._queryset[mark]
        except IndexError:
            # TODO: Need to find largest value
            raise MissingBorderObjectException()

    def _parameters_from_queryset(self):
        if not self.border_obj:
            self.border_obj = self._get_edge_item()

        ordering = self.get_ordering()
        parameters = []
        for field_name in ordering:
            parameter_ascending = self.ascending

            if field_name[0] == '-':
                parameter_ascending = not parameter_ascending
            field = self._name_to_field(field_name)

            parameter = CursorParameter(
                field.get_attname(),
                value=getattr(self.border_obj, field.get_attname()),
                ascending=parameter_ascending,
            )
            parameters.append(parameter)
        return parameters

    def _queryset_from_parameters(self):
        params = []
        stacked_params = Q()
        try:
            for parameter in self.parameters:
                params.append(parameter.filter_param & stacked_params)
                stacked_params &= parameter.eq_param
        except MissingBorderObjectException:
            return self._queryset.none()
        queryset = self._queryset._clone()
        queryset.query.clear_limits()
        if params:
            queryset = queryset.filter(reduce(operator.or_, params))
        ordering = self.get_ordering()
        qs = queryset.order_by(*ordering)
        # Remove redundant query where clauses

        # qs.query = reduce_redundant_clauses(qs.query)

        return qs

    def _get_queryset(self):
        return self._queryset_from_parameters()

    def _set_queryset(self, value):
        self._queryset = value

    queryset = property(_get_queryset, _set_queryset)

    def _get_parameters(self):
        if not self._parameters:
            self._parameters = self._parameters_from_queryset()
        return self._parameters

    def _set_parameters(self, value):
        self._parameters = value

    parameters = property(_get_parameters, _set_parameters)

    def _get_token(self):
        raise NotImplementedError(
            "Need to implement `_get_token` in a sub-class")

    def _set_token(self, token):
        raise NotImplementedError(
            "Need to implement `_set_token` in a sub-class")

    token = lazy_property(_get_token, _set_token)

    def __str__(self):
        return self.token

    def __repr__(self):
        param_names = ['queryset', 'border_obj', 'inclusive', 'ascending',
                       'token']
        params = ["{}={}".format(name, repr(getattr(self, name)))
                  for name in param_names if getattr(self, name)]

        return "{cls}({params})".format(
            cls=self.__class__.__name__,
            params=', '.join(params)
        )

    def __eq__(self, other):
        return self.parameters == other.parameters
