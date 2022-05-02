#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import collections
import enum
import sys

import uxf


def main():
    verbose = True
    if len(sys.argv) > 1 and sys.argv[1] in {'-q', '--quiet'}:
        verbose = False

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

    uxf.AutoConvertSequences = True
    uxf.add_converter(NumKind, to_str=lambda k: f'%NumKind {k.name}',
                      from_str=numkind_from_str)
    uxf.add_converter(State, to_str=lambda s: f'%State {s.value}',
                      from_str=state_from_str)
    uxf.add_converter(Align, to_str=lambda a: f'%{a.name}%',
                      from_str=align_from_str)
    uxf.add_converter(complex, to_str=lambda c: f'%{c}',
                      from_str=complex_from_str)
    uxf.add_converter(Symbols, to_str=lambda s: s.name,
                      from_str=symbol_from_str)

    uxd1 = uxf.Uxf(d)
    uxt1 = uxd1.dumps()
    uxd2 = uxf.loads(uxt1)
    uxt2 = uxd2.dumps()
    check_types(1, uxd1.data, verbose)
    check_types(2, uxd2.data, verbose)
    if uxt1 != uxt2:
        fail('test_converters • loads()/dumps() FAIL', verbose)
    if verbose:
        print(uxt1, end='')
        print('test_converters • loads()/dumps() OK')


def check_types(which, d, verbose):
    check_all_types(which, NumKind, d['numkind'], verbose)
    check_all_types(which, State, d['state'], verbose)
    check_all_types(which, Align, d['align'], verbose)
    check_all_types(which, Symbols, d['symbols'], verbose)
    check_all_types(which, complex, d['complex'], verbose)


def check_all_types(which, Class, seq, verbose):
    for x in seq:
        if not isinstance(x, Class):
            fail(f'test_converters • #{which} {Class.__name__} types '
                 'not preserved FAIL')
    else:
        if verbose:
            print(f'test_converters • #{which} {Class.__name__} OK')


def fail(message, verbose):
    if verbose:
        print(message)
    sys.exit(1)


def complex_from_str(s):
    if s.startswith('%(') and s.endswith('j)'):
        try:
            return complex(s[1:]), True
        except ValueError:
            pass
    return None, False


def numkind_from_str(s):
    parts = s.split(None, 1)
    if len(parts) == 2 and parts[0] == '%NumKind':
        kind = NumKind.from_name(parts[1])
        if kind is not None:
            return kind, True
    return None, False


def state_from_str(s):
    parts = s.split(None, 1)
    if len(parts) == 2 and parts[0] == '%State':
        value = parts[1]
        for state in State:
            if state.value == value:
                return state, True
    return None, False


def align_from_str(s):
    if s.startswith('%') and s.endswith('%'):
        value = s[1:-1]
        for align in Align:
            if align.name == value:
                return align, True
    return None, False


class NumKind(enum.Enum):
    ARABIC = 1
    ROMAN = 2

    @classmethod
    def from_name(Class, name):
        name = name.upper()
        for kind in Class:
            if kind.name == name:
                return kind


class State(enum.Enum):
    BEGIN = 'begin'
    MIDDLE = 'middle'
    END = 'end'


class Align(enum.Enum):
    LEFT = enum.auto()
    CENTER = enum.auto()
    JUSTIFY = enum.auto()
    RIGHT = enum.auto()


@enum.unique
class Symbols(enum.IntEnum):
    DECIMAL = 0
    ROMAN = 1


def symbol_from_str(s):
    for symbol in Symbols:
        if symbol.name == s:
            return symbol, True
    return None, False


if __name__ == '__main__':
    main()
