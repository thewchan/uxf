#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
Tests and shows how to do one-way conversions of sets, frozensets, tuples,
and deques into a Uxf object, and how to handle round-trippable custom data
including enums, complex numbers, and a custom type.
'''

import collections
import enum
import sys


try:
    import os
    os.chdir(os.path.dirname(__file__)) # move to this file's dir
    sys.path.append('..')
    import uxf
    import eq
    os.chdir('../../testdata') # move to test data
finally:
    pass


def main():
    regression = False
    if len(sys.argv) > 1 and sys.argv[1] in {'-r', '--regression'}:
        regression = True

    d = {}
    d['set'] = set((1, 2, 3))
    d['frozenset'] = frozenset((2, 4, 8, 16))
    d['tuple'] = tuple('abcd')
    d['deque'] = collections.deque('EFGHIJK')
    d['numkind'] = frozenset([NumKind.ROMAN, NumKind.ARABIC])
    d['symbols'] = frozenset([Symbols.ROMAN, Symbols.DECIMAL])
    d['not enum'] = '%Not enum'
    d['not complex1'] = '%(Not complex)'
    d['not complex2'] = '%(18/4)'
    d['state'] = set((State.MIDDLE, State.BEGIN, State.END))
    d['align'] = (Align.LEFT, Align.CENTER, Align.JUSTIFY, Align.RIGHT)
    d['complex'] = (complex(-3.9), (8-7j), (1.3+.1j), # noqa: E226
                    complex(-1.2, -.3))
    d['MyType'] = (MyType('one', 1, False), MyType('one & one', 2, True))

    uxf.add_converter(NumKind, to_str=lambda k: f'%NumKind {k.name}',
                      from_str=numkind_from_str)
    uxf.add_converter(State, to_str=lambda s: f'%State {s.value}',
                      from_str=state_from_str)
    uxf.add_converter(Align, to_str=lambda a: f'%{a.name}%',
                      from_str=align_from_str)
    uxf.add_converter(complex, to_str=lambda c: f'©{c}',
                      from_str=complex_from_str)
    uxf.add_converter(Symbols, to_str=lambda s: s.name,
                      from_str=symbol_from_str)
    uxf.add_converter(MyType, to_str=mytype_to_str,
                      from_str=mytype_from_str)

    uxo1 = uxf.Uxf(d)
    uxt1 = uxo1.dumps()
    uxo2 = uxf.loads(uxt1)
    uxt2 = uxo2.dumps()
    total = ok = 0
    total, ok = check_types(total, ok, 1, uxo1.data, regression)
    total, ok = check_types(total, ok, 2, uxo2.data, regression)
    total += 1
    if uxt1 == uxt2:
        ok += 1
    elif not regression:
        print('test_converters • loads()/dumps() FAIL')
    total += 1
    if eq.eq(uxo1, uxo2):
        ok += 1
    elif not regression:
        print('test_converters • eq() FAIL')
    if not regression:
        print(uxt1, end='')
        print('test_converters • eq() & loads()/dumps() OK')
    else:
        print(f'total={total} ok={ok}')


def check_types(total, ok, which, d, regression):
    total, ok = check_all_types(total, ok, which, NumKind, d['numkind'],
                                regression)
    total, ok = check_all_types(total, ok, which, State, d['state'],
                                regression)
    total, ok = check_all_types(total, ok, which, Align, d['align'],
                                regression)
    total, ok = check_all_types(total, ok, which, Symbols, d['symbols'],
                                regression)
    total, ok = check_all_types(total, ok, which, complex, d['complex'],
                                regression)
    return total, ok


def check_all_types(total, ok, which, Class, seq, regression):
    for x in seq:
        total += 1
        if isinstance(x, Class):
            ok += 1
        elif not regression:
            print(f'test_converters • #{which} expected {Class.__name__} '
                  f'got {x.__class__.__name__} {x!r} FAIL')
    else:
        if not regression:
            print(f'test_converters • #{which} {Class.__name__} OK')
    return total, ok


# to_str=lambda c: f'©{c}'
def complex_from_str(s):
    if s.startswith('©(') and s.endswith('j)'):
        try:
            return complex(s[1:]), True
        except ValueError:
            pass
    return None, False


# 4 different enums with 4 different approaches to from_str
# (followed by a custom type and its own to_str and from_str)


# This is needed to allow enums to be compared which is needed because we
# want to compare Uxf's that contain sets of enums for equality .
class OrderedEnum(enum.Enum):

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class NumKind(OrderedEnum):
    ARABIC = 1
    ROMAN = 2

    @classmethod
    def from_name(Class, name):
        name = name.upper()
        for kind in Class:
            if kind.name == name:
                return kind


# to_str=lambda k: f'%NumKind {k.name}'
def numkind_from_str(s):
    parts = s.split(None, 1)
    if len(parts) == 2 and parts[0] == '%NumKind':
        kind = NumKind.from_name(parts[1])
        if kind is not None:
            return kind, True
    return None, False


class State(OrderedEnum):
    BEGIN = 'begin'
    MIDDLE = 'middle'
    END = 'end'


# to_str=lambda s: f'%State {s.value}'
def state_from_str(s):
    parts = s.split(None, 1)
    if len(parts) == 2 and parts[0] == '%State':
        value = parts[1]
        for state in State:
            if state.value == value:
                return state, True
    return None, False


class Align(OrderedEnum):
    LEFT = enum.auto()
    CENTER = enum.auto()
    JUSTIFY = enum.auto()
    RIGHT = enum.auto()


# to_str=lambda a: f'%{a.name}%'
def align_from_str(s):
    if s.startswith('%') and s.endswith('%'):
        value = s[1:-1]
        for align in Align:
            if align.name == value:
                return align, True
    return None, False


@enum.unique
class Symbols(OrderedEnum):
    DECIMAL = 0
    ROMAN = 1


# to_str=lambda s: s.name
def symbol_from_str(s):
    for symbol in Symbols:
        if symbol.name == s:
            return symbol, True
    return None, False


class MyType:

    def __init__(self, name: str, code: int, flag: bool):
        self.name = name
        self.code = code
        self.flag = flag


    def __eq__(self, other): # needed if we want to compare Uxf objects
        if not isinstance(other, self.__class__):
            return False
        return (self.name == other.name and self.code == other.code and
                self.flag == other.flag)


    def __repr__(self):
        return (f'{self.__class__.__name__}({self.name!r}, {self.code!r}, '
                f'{self.flag!r})')


def mytype_to_str(m):
    return f'@MyType {m.flag!r} {m.code!r} {m.name}'


def mytype_from_str(s):
    parts = s.split(None, 3)
    if len(parts) == 4 and parts[0] == '@MyType': # NOTE Safe if we sanitize
        if parts[1] not in {'True', 'False'}:
            return None, False
        flag = parts[1] == 'True'
        try:
            code = int(parts[2])
        except ValueError:
            return None, False
        name = parts[3]
        return MyType(name, code, flag), True
    return None, False



if __name__ == '__main__':
    main()
