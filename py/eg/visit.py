#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
The visit function calls the given function on every value in the given data
(which can be a Uxf object or a single list, List, dict, Map, or Table).
'''

import collections
import datetime
import enum
import os
import sys

try:
    import uxf
except ImportError: # needed for development
    sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
    import uxf

try:
    from dateutil.parser import isoparse
except ImportError:
    isoparse = None


UTF8 = 'utf-8'
MAX_IDENTIFIER_LEN = 60
MAX_LIST_IN_LINE = 10
MAX_SHORT_LEN = 32
_KEY_TYPES = frozenset({'int', 'date', 'datetime', 'str', 'bytes'})
_VALUE_TYPES = frozenset(_KEY_TYPES | {'bool', 'real'})
_ANY_VALUE_TYPES = frozenset(_VALUE_TYPES | {'list', 'map', 'table'})
_BOOL_FALSE = frozenset({'no', 'false'})
_BOOL_TRUE = frozenset({'yes', 'true'})
_CONSTANTS = frozenset(_BOOL_FALSE | _BOOL_TRUE)
_BAREWORDS = frozenset(_ANY_VALUE_TYPES | _CONSTANTS)
TYPENAMES = frozenset(_ANY_VALUE_TYPES | {'null'})
_MISSING = object()


class Error(Exception):
    pass


def visit(function, value):
    '''Calls the given function for every every value in the Uxf object (or
    the list, List, dict, Map, or Table, value if given). The function is
    called with one or two arguments, the first being a ValueType and the
    second (where given) a value.

        import uxf
        import visit
        u = uxf.load('file.uxf')
        visit.visit(print, u)
        # -or-
        for value in u.data: # if u's data is a List or Table
            visit.visit(print, value)

    See also the ValueType enum.
    '''
    if value is None:
        function(ValueType.NULL)
    elif isinstance(value, uxf.Uxf):
        _visit_uxf(function, value)
    elif isinstance(value, (tuple, list, uxf.List)):
        _visit_list(function, value)
    elif isinstance(value, (dict, uxf.Map)):
        _visit_map(function, value)
    elif isinstance(value, uxf.Table):
        _visit_table(function, value)
    elif isinstance(value, bool):
        function(ValueType.BOOL, value)
    elif isinstance(value, int):
        function(ValueType.INT, value)
    elif isinstance(value, float):
        function(ValueType.REAL, value)
    elif isinstance(value, datetime.datetime):
        function(ValueType.DATE_TIME, value)
    elif isinstance(value, datetime.date):
        function(ValueType.DATE, value)
    elif isinstance(value, str):
        function(ValueType.STR, value)
    elif isinstance(value, (bytes, bytearray)):
        function(ValueType.BYTES, value)
    elif isinstance(value, uxf.TClass):
        pass # ignore
    else:
        if hasattr(value, 'totuple'):
            visit(function, value.totuple())
        else:
            raise Error('can\'t visit values of type '
                        f'{value.__class__.__name__}: {value!r}')


def _visit_uxf(function, uxo):
    info = UxfInfo(uxo.custom, uxo.comment, uxo.tclasses)
    function(ValueType.UXF_BEGIN, info)
    visit(function, uxo.data)
    function(ValueType.UXF_END, Tag(info.custom))


def _visit_list(function, lst):
    info = ListInfo(getattr(lst, 'comment', None),
                    getattr(lst, 'vtype', None))
    function(ValueType.LIST_BEGIN, info)
    for element in lst:
        visit(function, element)
    function(ValueType.LIST_END)


def _visit_map(function, d):
    info = MapInfo(getattr(d, 'comment', None), getattr(d, 'ktype', None),
                   getattr(d, 'vtype', None))
    function(ValueType.MAP_BEGIN, info)
    for key, element in d.items():
        function(ValueType.MAP_KEY)
        visit(function, key)
        function(ValueType.MAP_VALUE)
        visit(function, element)
    function(ValueType.MAP_END)


def _visit_table(function, table):
    info = TableInfo(getattr(table, 'comment', None),
                     getattr(table, 'ttype', None),
                     getattr(table, 'tclass', None))
    function(ValueType.TABLE_BEGIN, info)
    for record in table:
        rtype = record.__class__.__name__
        if rtype.startswith('UXF_'):
            rtype = rtype[3:]
        tag = Tag(rtype)
        function(ValueType.ROW_BEGIN, tag)
        for item in record:
            visit(function, item)
        function(ValueType.ROW_END, tag)
    function(ValueType.TABLE_END, Tag(info.ttype))


@enum.unique
class ValueType(enum.Enum):
    UXF_BEGIN = enum.auto()
    UXF_END = enum.auto()
    LIST_BEGIN = enum.auto()
    LIST_END = enum.auto()
    MAP_BEGIN = enum.auto()
    MAP_KEY = enum.auto()
    MAP_VALUE = enum.auto()
    MAP_END = enum.auto()
    TABLE_BEGIN = enum.auto()
    TABLE_END = enum.auto()
    ROW_BEGIN = enum.auto()
    ROW_END = enum.auto()
    BOOL = enum.auto()
    INT = enum.auto()
    REAL = enum.auto()
    DATE = enum.auto()
    DATE_TIME = enum.auto()
    STR = enum.auto()
    BYTES = enum.auto()
    NULL = enum.auto()


UxfInfo = collections.namedtuple('UxfInfo', 'custom comment tclasses')
ListInfo = collections.namedtuple('ListInfo', 'comment vtype')
MapInfo = collections.namedtuple('MapInfo', 'comment ktype vtype')
TableInfo = collections.namedtuple('TableInfo', 'comment ttype tclass')
Tag = collections.namedtuple('Tag', 'name')
