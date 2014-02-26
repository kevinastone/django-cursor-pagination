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


def _unroll_where_clause(where):
    """
    Attempts to unroll redundantly nested where clauses (like AND( AND( something = 1)))
    """
    # Look to see if we are just nested in single branch nodes
    while getattr(where, 'children', None):
        if len(where.children) != 1:
            break
        child = where.children[0]
        if isinstance(child, (list, tuple)):
            where = child
            break
        elif where.connector != child.connector:
            break
        where = child
    return where


def _reduce_redundant_clauses(where):
    clauses = defaultdict(list)
    other_clauses = []
    duplicate_found = False

    where = _unroll_where_clause(where)

    if not hasattr(where, 'children'):
        return where

    for child in where.children:
        child = _unroll_where_clause(child)
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
    """
    Attempts to remove redundant where clauses that are superseded by more stringest clauses.

    For Example: "select * from example_table where id > 1 and id > 2"
    Can be reduced to: "select * from example_table where id > 2"
    """

    query = query.clone()
    where = _reduce_redundant_clauses(query.where)
    if isinstance(where, (list, tuple)):
        constraint, lookup_type, negation, value = where
        where = query.where_class()
        clause = (constraint, lookup_type, value)
        where.add(clause, AND)
    query.where = where

    return query
