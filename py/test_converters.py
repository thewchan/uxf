#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import collections
import enum
import sys

import uxf


def main():
    d = {}
    d['set'] = set((1, 2, 3))
    d['frozenset'] = frozenset((2, 4, 8, 16))
    d['tuple'] = tuple('abcd')
    d['deque'] = collections.deque('EFGHIJK')
    d['numkind'] = NumKind.ROMAN
    uxf.AutoConvertSequences = True
    uxf.add_converter(NumKind, to_str=numkind_to_str,
                      from_str=numkind_from_str)
    uxd1 = uxf.Uxf(d)
    uxt1 = uxd1.dumps()
    uxd2 = uxf.loads(uxt1)
    uxt2 = uxd2.dumps()
    if uxt1 != uxt2:
        sys.exit(1) #
    print(uxt2)
    if False: # TODO on error
        sys.exit(1)


def numkind_to_str(kind):
    return f'%NumKind {kind.name}'


def numkind_from_str(s):
    parts = s.split(None, 1)
    if len(parts) == 2 and parts[0] == '%NumKind':
        kind = NumKind.from_name(parts[1])
        if kind is not None:
            return kind, True
    return None, False


class NumKind(enum.Enum):
    DECIMAL = 1
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


if __name__ == '__main__':
    main()
