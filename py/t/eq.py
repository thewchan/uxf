#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import collections
import math
import pprint


try:
    import os
    import sys
    os.chdir(os.path.dirname(__file__)) # move to this file's dir
    sys.path.append('..')
    import uxf
finally:
    pass


def eq(a, b, *, ignore_comments=False, ignore_custom=False,
       ignore_types=False, debug=False):
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
        return (not bool(s) and not bool(t)) or s == t

    def eq_comment(s, t):
        '''Returns True if s and t are both either empty or None or have the
        same nonempty text; otherwise False.'''
        return (not bool(s) and not bool(t)) or s == t

    kwargs = dict(ignore_comments=ignore_comments,
                  ignore_custom=ignore_custom, ignore_types=ignore_types,
                  debug=debug)

    if isinstance(a, uxf.Uxf):
        if not ignore_custom and not eq_custom(a.custom, b.custom):
            if debug:
                _fail('custom', a.custom, b.custom)
            return False
        if not ignore_comments and not eq_comment(a.comment, b.comment):
            if debug:
                _fail('Uxf.comment', a.comment, b.comment)
            return False
        if not ignore_types and not eq(a.ttypes, b.ttypes, **kwargs):
            if debug:
                _fail('Uxf.ttypes', a.ttypes, b.ttypes)
            return False
        if not eq(a.data, b.data, **kwargs):
            if debug:
                _fail('Uxf.data', a.data, b.data)
            return False
        return True
    if isinstance(a, uxf.List):
        if not ignore_comments and not eq_comment(a.comment, b.comment):
            if debug:
                _fail('List.comment', a.comment, b.comment)
            return False
        if not ignore_types and a.vtype != b.vtype:
            if debug:
                _fail('List.vtype', a.vtype, b.vtype)
            return False
        if not eq(a.data, b.data, **kwargs):
            if debug:
                _fail('List.data', a.data, b.data)
            return False
        return True
    if isinstance(a, uxf.Map):
        if not ignore_comments and not eq_comment(a.comment, b.comment):
            if debug:
                _fail('Map.comment', a.comment, b.comment)
            return False
        if not ignore_types:
            if a.ktype != b.ktype:
                if debug:
                    _fail('Map.ktype', a.ktype, b.ktype)
                return False
            if a.vtype != b.vtype:
                if debug:
                    _fail('Map.vtype', a.vtype, b.vtype)
                return False
        if not eq(a.data, b.data, **kwargs):
            if debug:
                _fail('Map.data', a.data, b.data)
            return False
        return True
    if isinstance(a, uxf.TType):
        if not ignore_comments and not eq_comment(a.comment, b.comment):
            if debug:
                _fail('TType.comment', a.comment, b.comment)
            return False
        if a.name != b.name:
            if debug:
                _fail('TType.name', a.name, b.name)
            return False
        if len(a.fields) != len(b.fields):
            if debug:
                _fail('TType.fields (len)', a.fields, b.fields)
            return False
        for afield, bfield in zip(a.fields, b.fields):
            if afield.name != bfield.name:
                if debug:
                    _fail('TType.fields (name)', afield, bfield)
                return False
            if not ignore_types and afield.vtype != bfield.vtype:
                if debug:
                    _fail('TType.fields (vtype)', afield, bfield)
                return False
        return True
    if isinstance(a, uxf.Table):
        if not ignore_comments and not eq_comment(a.comment, b.comment):
            if debug:
                _fail('Table.comment', a.comment, b.comment)
            return False
        if a.name != b.name:
            if debug:
                _fail('Table.name', a.name, b.name)
            return False
        if not ignore_types and not eq(a.ttype, b.ttype, **kwargs):
            if debug:
                _fail('Table.ttype', a.ttype, b.ttype)
            return False
        for i, (arec, brec) in enumerate(zip(iter(a), iter(b))):
            if not eq(arec, brec, **kwargs):
                if debug:
                    _fail(f'Table[{i}]', arec, brec)
                return False
        return True
    if isinstance(a, (list, tuple, collections.deque)):
        if len(a) != len(b):
            if debug:
                _fail('List (len)', a, b)
            return False
        for i, (avalue, bvalue) in enumerate(zip(a, b)):
            if not eq(avalue, bvalue, **kwargs):
                if debug:
                    _fail(f'List[{i}]', avalue, bvalue)
                return False
        return True
    if isinstance(a, (set, frozenset)):
        if len(a) != len(b):
            if debug:
                _fail('set (len)', a, b)
            return False
        for i, (avalue, bvalue) in enumerate(zip(sorted(a), sorted(b))):
            if not eq(avalue, bvalue, **kwargs):
                if debug:
                    _fail('sorted(set)[i]', avalue, bvalue)
                return False
        return True
    if isinstance(a, dict):
        if len(a) != len(b):
            if debug:
                _fail('dict (len)', a, b)
            return False
        for (akey, avalue), (bkey, bvalue) in zip(
                sorted(a.items(), key=by_key),
                sorted(b.items(), key=by_key)):
            if akey != bkey:
                if debug:
                    _fail('dict (key)', akey, bkey)
                return False
            if not eq(avalue, bvalue, **kwargs):
                if debug:
                    _fail('dict (value)', avalue, bvalue)
                return False
        return True
    if isinstance(a, float):
        if not math.isclose(a, b):
            if debug:
                _fail('float', a, b)
            return False
        return True
    if a != b:
        if debug:
            _fail('generic', a, b)
        return False
    return True


def _fail(where, a, b):
    print(f'{where} a != b {a == b}')
    print()
    print('type(a)', type(a))
    print()
    _pprint(a)
    print()
    print('type(b)', type(b))
    print()
    _pprint(b)
    raise SystemExit()


def _pprint(x):
    if isinstance(x, uxf.Table):
        _print_table(x)
    elif isinstance(x, uxf.List):
        _print_list(x)
    else:
        pprint.pprint(x)


def _print_table(t):
    print('name', t.name)
    print('comment', t.comment)
    print('fields:')
    pprint.pprint(t.fields)
    print('records:')
    for record in t:
        _pprint(record)


def _print_list(t):
    print('comment', t.comment)
    print('values:')
    for value in t:
        _pprint(value)