#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
Tests and shows how to do one-way conversions of sets, frozensets, tuples,
and deques into a Uxf object, and how to handle round-trippable custom data
including enums, complex numbers, and a custom type.
'''

import sys
import os


try:
    PATH = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(os.path.join(PATH, '../')))
    import uxf
    os.chdir(os.path.join(PATH, '../../testdata')) # move to test data
finally:
    pass


def main():
    regression = False
    if len(sys.argv) > 1 and sys.argv[1] in {'-r', '--regression'}:
        regression = True
    total = ok = 0

    t = uxf.Table()
    t.tclass = uxf.tclass('point', 'x', 'y')
    # append
    t.append((1, -6))
    t.append((3, 21))
    t.append((-4, 8))
    t.append((5, 17))
    # insert
    t.insert(1, (-2, 19))
    total += 1
    # __getitem__
    p = t[3]
    if p.x == -4 and p.y == 8:
        ok += 1
    # __setitem__
    t[1] = (-20, 191)
    total += 1
    p = t[1]
    if p.x == -20 and p.y == 191:
        ok += 1
    # len()
    total += 1
    if len(t) == 5:
        ok += 1
    # __delitem__
    del t[3]
    total += 1
    if len(t) == 4:
        ok += 1
    # __iter__
    total += 1
    expected = [t.RecordClass(*p)
                for p in [(1, -6), (-20, 191), (3, 21), (5, 17)]]
    if list(t) == expected:
        ok += 1
    # properties
    total += 1
    if t.ttype == 'point':
        ok += 1
    total += 1
    if t.fields == [uxf.Field('x'), uxf.Field('y')]:
        ok += 1

    # errors (see test_errors.py for 320 340
    try:
        total += 1
        e = 370 # must preced 360
        t.append((-7, -8, -9))
        fail(f'test_table • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    t._append(-99)

    try:
        total += 1
        e = 360
        t.append((-7, -8))
        fail(f'test_table • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    print(f'total={total} ok={ok}')


def got_error(code, err, regression):
    err = str(err)
    code = f'#{code}:'
    if code not in err:
        fail(f'test_errors • expected {code} got, {err!r} FAIL',
             regression)
        return 0
    return 1


def fail(message, regression):
    if not regression:
        print(message)


if __name__ == '__main__':
    main()
