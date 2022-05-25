#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import os
import sys

try:
    PATH = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(os.path.join(PATH, '../')))
    import uxf
finally:
    pass


def main():
    regression = False
    if len(sys.argv) > 1 and sys.argv[1] in {'-r', '--regression'}:
        regression = True
    total = ok = 0

    fieldnames = ('width', 'height')
    Record = uxf._make_record_class('Record', *fieldnames)
    r = Record(-7, 29)

    total += 1
    if repr(r) == 'Record(-7, 29)':
        ok += 1
    elif not regression:
        print('fail #1')

    total += 1
    if r.width == r[0] == -7 and r.height == r[1] == 29:
        ok += 1
    elif not regression:
        print('fail #2')
    r.width *= -2
    r[1] -= 3

    total += 1
    if repr(r) == 'Record(14, 26)':
        ok += 1
    elif not regression:
        print('fail #3')

    total += 1
    if r.width == r[0] == 14 and r.height == r[1] == 26:
        ok += 1
    elif not regression:
        print('fail #4')

    total += 1
    try:
        print(r[2])
        if not regression:
            print('expected IndexError')
    except IndexError:
        ok += 1

    total += 1
    try:
        print(r.missing)
        if not regression:
            print('expected AttributeError')
    except AttributeError:
        ok += 1

    total += 1
    try:
        Record(2, 3, 4)
        if not regression:
            print('expected TypeError')
    except TypeError:
        ok += 1

    total += 1
    if repr(Record()) == 'Record(None, None)':
        ok += 1
    elif not regression:
        print('fail #5')

    total += 1
    if repr(Record(2)) == 'Record(2, None)':
        ok += 1
    elif not regression:
        print('fail #6')

    total += 1
    if repr(Record(2, 3)) == 'Record(2, 3)':
        ok += 1
    elif not regression:
        print('fail #7')

    total += 1
    if tuple(Record(-8, 17)) == (-8, 17):
        ok += 1
    elif not regression:
        print('fail #8')

    print(f'total={total} ok={ok}')


if __name__ == '__main__':
    main()
