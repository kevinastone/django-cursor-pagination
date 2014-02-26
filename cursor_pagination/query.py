from __future__ import absolute_import

from collections import defaultdict

from django.db.models.sql.where import Constraint, AND, OR


REDUCTION_OPERATIONS = {
    AND: {
        'gt': max,
        'gte': max,
        'lt': min,
        'lte': min,
    },
    OR: {
        'gt': min,
        'gte': min,
        'lt': max,
        'lte': max,
    }
}


def _reduce_redundant_clauses(where):
    clauses = defaultdict(list)
    other_clauses = []
    duplicate_found = False

    for child in where.children:
        if isinstance(child, (list, tuple)) and isinstance(child[0], Constraint):
            constraint, lookup_type, negation, value = child
            constraint_params = (constraint.alias, constraint.col, constraint.field)
            clauses[(constraint_params, lookup_type)].append(value)
            duplicate_found = True
        else:
            other_clauses.append(_reduce_redundant_clauses(child))

    if not duplicate_found:
        return where

    new_where = where.__class__()
    for child in other_clauses:
        new_where.add(child, where.connector)

    for (constraint_params, lookup_type), values in clauses.items():
        constraint = Constraint(*constraint_params)
        reduction_operator = REDUCTION_OPERATIONS[where.connector].get(lookup_type)
        if reduction_operator:
            try:
                values = [reduction_operator(values)]
            except:
                # If we can't reduce, just use the original clauses
                pass
        for value in values:
            child = (constraint, lookup_type, value)
            new_where.add(child, where.connector)

    return new_where


def reduce_redundant_clauses(query):

    query = query.clone()
    query.where = _reduce_redundant_clauses(query.where)

    return query
