#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

# TODO rip out fixtypes and just report type errors; drop _Typecheck and
# print errors as they are encountered.


import collections
import datetime
import sys

try:
    import uxf
except ImportError: # needed for development
    import importer
    uxf = importer.import_module('uxf', '../uxf.py')


def main():
    if len(sys.argv) < 2 or sys.argv[1] in {'-h', '--help'}:
        raise SystemExit(
            '''usage: typecheck.py <uxf-filename>
Checks any given types against the actual values and gives warnings if
appropriate.''')
    uxo = uxf.load(sys.argv[1])
    _typecheck(uxo.data, 'collection', ttypes=uxo.ttypes)



def _typecheck(value, vtype, *, ttypes=None):
    if value is None or not vtype: # null is always a valid value
        return _Typecheck(value, False, True)
    if isinstance(value, uxf.Table):
        reply = _typecheck_table(value, vtype, ttypes)
        if reply is not None:
            return reply
    elif isinstance(value, uxf.List):
        reply = _typecheck_list(value, ttypes)
        if reply is not None:
            return reply
    elif isinstance(value, uxf.Map):
        reply = _typecheck_map(value, ttypes)
        if reply is not None:
            return reply
    else:
        classes = _TYPECHECK_CLASSES.get(vtype)
        if not isinstance(value, classes) and vtype != 'collection':
            if isinstance(value, str) and vtype in {'bool', 'int', 'real',
                                                    'date', 'datetime'}:
                print(
                    f'Typecheck:#10:expected a {vtype}, got str: {value!r}')
                new_value = uxf.naturalize(value)
                return _Typecheck(new_value, isinstance(new_value, classes),
                                  True)
            if isinstance(value, int) and vtype == 'real':
                return _Typecheck(float(value), True, True)
            if isinstance(value, float) and vtype == 'int':
                return _Typecheck(int(value), True, True)
        if isinstance(value, classes):
            return _Typecheck(value, False, True)
        atype = _TYPECHECK_ATYPES.get(type(value))
        print(f'Typecheck:#10:expected a {vtype}, got {atype}')
        return _Typecheck(value, False, False)


def _typecheck_list(data, ttypes, fixtypes=False):
    for i in range(len(data)):
        value = data[i]
        check = _typecheck(value, data.vtype, ttypes=ttypes,
                           fixtypes=fixtypes)
        if check.fixed:
            value = check.value
            data[i] = value


def _typecheck_map(data, ttypes, fixtypes=False):
    keys = list(data.keys())
    for key in keys:
        value = data[key]
        check = _typecheck(key, data.ktype, ttypes=ttypes,
                           fixtypes=fixtypes)
        if check.fixed: # unlikely
            del data[key]
            key = check.value
            data[key] = value
        check = _typecheck(value, data.vtype, ttypes=ttypes,
                           fixtypes=fixtypes)
        if check.fixed:
            value = check.value
            data[key] = value



def _typecheck_table(data, vtype, ttypes, fixtypes):
    for row in range(len(data.records)):
        columns = len(data.records[row])
        if columns != len(data.fields):
            print(f'Typecheck:#20:expected {len(data.fields)} fields, '
                  f'got {columns}')
        for column in range(columns):
            if column < len(data.fields):
                field = data.field(column)
                value = data.records[row][column]
                check = _typecheck(value, field.vtype, ttypes=ttypes,
                                   fixtypes=fixtypes)
                if check.fixed:
                    value = check.value
                    data.records[row][column] = value
    if vtype == 'collection':
        return _Typecheck(data, False, True) # any collection is ok
    if ttypes is None:
        print(
            f'Typecheck:#30:got value of unknown type {data.ttype.name}')
        return _Typecheck(data, False, False)
    ttype = ttypes.get(data.ttype.name)
    if vtype == ttype.name:
        return _Typecheck(data, False, True)
    else:
        print(f'Typecheck:#40:expected a value of type {vtype}, got '
              f'{data.ttype.name}')
        return _Typecheck(data, False, False)


_Typecheck = collections.namedtuple('_Typecheck', 'value ok')

_TYPECHECK_CLASSES = dict(
    collection=(uxf.List, uxf.Map, uxf.Table), bool=bool,
    bytes=(bytes, bytearray), date=datetime.date,
    datetime=datetime.datetime, int=int, list=uxf.List, map=uxf.Map,
    real=float, str=str, table=uxf.Table)
_TYPECHECK_ATYPES = {
    bool: 'bool', bytearray: 'bytes', bytes: 'bytes',
    datetime.date: 'date', datetime.datetime: 'datetime', float: 'real',
    int: 'int', uxf.List: 'list', uxf.Map: 'map', str: 'str',
    uxf.Table: 'table', type(None): '?'}


if __name__ == '__main__':
    main()
