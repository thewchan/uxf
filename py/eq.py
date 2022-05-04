#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import collections
import math

import uxf


def eq(a, b, *, ignore_comments=False, ignore_custom=False):
    '''This function is provided primarily for use in automated testing.
    Returns True if a and b are eq Uxf's, Tables, Lists, or Maps;
    otherwise returns False. This function compares all the values (and
    comments) recursively, so is potentially expensive.
    This function requires that values in sets are sortable.
    Note also that if custom types are stored they will compare as != unless
    they have an __eq__ method.
    '''
    def by_key(item):
        return str(item[0])

    def eq_custom(s, t):
        '''Returns True if s and t are both either empty or None or have the
        same nonempty text; otherwise False.'''
        return ignore_custom or ((not bool(s) and not bool(t)) or s == t)

    def eq_comment(s, t):
        '''Returns True if s and t are both either empty or None or have the
        same nonempty text; otherwise False.'''
        return ignore_comments or ((not bool(s) and not bool(t)) or s == t)

    if isinstance(a, uxf.Uxf):
        return (eq(a.data, b.data) and
                eq_custom(a.custom, b.custom) and
                eq_comment(a.comment, b.comment) and
                eq(a.ttypes, b.ttypes))
    if isinstance(a, uxf.List):
        return (eq(a.data, b.data) and
                eq_comment(a.comment, b.comment) and
                a.vtype == b.vtype)
    if isinstance(a, uxf.Map):
        return (eq(a.data, b.data) and
                eq_comment(a.comment, b.comment) and
                a.ktype == b.ktype and a.vtype == b.vtype)
    if isinstance(a, uxf.TType):
        if a.name != b.name or not eq_comment(a.comment, b.comment):
            return False
        if len(a.fields) != len(b.fields):
            return False
        for afield, bfield in zip(a.fields, b.fields):
            if afield.name != bfield.name or afield.vtype != bfield.vtype:
                return False
        return True
    if isinstance(a, uxf.Table):
        if (not eq(a.ttype, b.ttype) or a.name != b.name or
                not eq_comment(a.comment, b.comment)):
            return False
        for arec, brec in zip(iter(a), iter(b)):
            if not eq(arec, brec):
                return False
        return True
    if isinstance(a, (list, tuple, collections.deque)):
        if len(a) != len(b):
            return False
        for avalue, bvalue in zip(a, b):
            if not eq(avalue, bvalue):
                return False
        return True
    if isinstance(a, (set, frozenset)):
        if len(a) != len(b):
            return False
        for avalue, bvalue in zip(sorted(a), sorted(b)):
            if not eq(avalue, bvalue):
                return False
        return True
    if isinstance(a, dict):
        if len(a) != len(b):
            return False
        for (akey, avalue), (bkey, bvalue) in zip(
                sorted(a.items(), key=by_key),
                sorted(b.items(), key=by_key)):
            if akey != bkey:
                return False
            if not eq(avalue, bvalue):
                return False
        return True
    if isinstance(a, float):
        return math.isclose(a, b)
    return a == b
