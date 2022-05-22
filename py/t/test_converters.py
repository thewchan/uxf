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
import os


try:
    PATH = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(os.path.join(PATH, '../')))
    import uxf
    import eq
    os.chdir(os.path.join(PATH, '../../testdata')) # move to test data
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
    d['state'] = set((State.MIDDLE, State.BEGIN, State.END))
    d['align'] = (Align.LEFT, Align.CENTER, Align.JUSTIFY, Align.RIGHT)
    d['complex'] = (complex(-3.9), (8-7j), (1.3+.1j), # noqa: E226
                    complex(-1.2, -.3))
    d['MyType'] = (MyType('one', 1, False), MyType('one & one', 2, True))

    def complex_from_str(s):
        try:
            return complex(f'({s}j)')
        except ValueError:
            return None

    uxf.add_converter('complex', to_str=lambda c: f'{c.real}{c.imag:+}',
                      from_str=complex_from_str)
    uxf.add_converter('NumKind', to_str=lambda e: e.name,
                      from_str=lambda n: NumKind.from_name(n))
    uxf.add_converter('State', to_str=lambda e: e.name,
                      from_str=state_from_str)
    uxf.add_converter('Align', to_str=lambda e: e.name,
                      from_str=align_from_str)
    uxf.add_converter('Symbols', to_str=lambda e: e.name,
                      from_str=symbol_from_str)
    uxf.add_converter('MyType', to_str=mytype_to_str,
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
        #################################### TODO BEGIN
        with open('/tmp/1', 'wt', encoding='utf8') as file:
            for k, v in uxo1.data.items():
                file.write(f'{k!r} = {v!r}\n')
        with open('/tmp/2', 'wt', encoding='utf8') as file:
            for k, v in uxo2.data.items():
                file.write(f'{k!r} = {v!r}\n')
        #################################### TODO END
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


class State(OrderedEnum):
    BEGIN = 'begin'
    MIDDLE = 'middle'
    END = 'end'


def state_from_str(s):
    for state in State:
        if state.value.upper() == s:
            return state


class Align(OrderedEnum):
    LEFT = enum.auto()
    CENTER = enum.auto()
    JUSTIFY = enum.auto()
    RIGHT = enum.auto()


def align_from_str(s):
    for align in Align:
        if align.name == s:
            return align


@enum.unique
class Symbols(OrderedEnum):
    DECIMAL = 0
    ROMAN = 1


def symbol_from_str(s):
    for symbol in Symbols:
        if symbol.name == s:
            return symbol


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
    return f'{m.flag!r} {m.code!r} {m.name}' if isinstance(m, MyType) else m


def mytype_from_str(s):
    parts = s.split(None, 3)
    if len(parts) == 3: # NOTE Safe if we sanitize
        if parts[0] not in {'True', 'False'}:
            return None, False
        flag = parts[0] == 'True'
        try:
            code = int(parts[1])
        except ValueError:
            return None, False
        name = parts[2]
        return MyType(name, code, flag)


if __name__ == '__main__':
    main()
