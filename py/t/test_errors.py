#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import collections
import sys


try:
    import os
    os.chdir(os.path.dirname(__file__)) # move to this file's dir
    sys.path.append('..')
    import uxf
    UXF_EXE = os.path.abspath('../uxf.py')
    os.chdir('../../testdata') # move to test data
finally:
    pass


def main():
    regression = False
    if len(sys.argv) > 1 and sys.argv[1] in {'-r', '--regression'}:
        regression = True
    total = ok = 0

    try:
        total += 1
        e = 100
        uxf.Uxf(collections.deque((1, 2, 3)))
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 110
        uxf.loads('not a uxf file', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 120
        uxf.loads('uxf\n', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 130
        uxf.loads('UXF 1.0\n', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 141
        uxf.loads('uxf 9.0\n', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 151
        uxf.loads('uxf 1.0x\n', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 160
        uxf.loads('uxf 1.0\n# Not a comment', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 170
        uxf.loads('uxf 1.0\n* invalid', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 180
        uxf.loads('uxf 1.0\n[# 123]', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 190
        uxf.loads('uxf 1.0\n[123 #<comment>]', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

#    table = uxf.Table(name='Pair', fields=('first', 'second'))
#
#    uxo = uxf.Uxf({})
#    uxo.data.append('key')
#    uxo.data.append('value')
#    try:
#        total += 1
#        e = 120
#        uxo.data.append(table)
#        fail(f'test_errors • #{e} FAIL', regression)
#    except uxf.Error as err:
#        ok += on_error(e, err, regression)
#    try:
#        total += 1
#        e = 130
#        uxo.data.append(3.8)
#        fail(f'test_errors • #{e} FAIL', regression)
#    except uxf.Error as err:
#        ok += on_error(e, err, regression)
#
#    try:
#        total += 1
#        e = 150
#        _ = uxf.Field('1st')
#        fail(f'test_errors • #{e} FAIL', regression)
#    except uxf.Error as err:
#        ok += on_error(e, err, regression)
#    try:
#        total += 1
#        e = 160
#        _ = uxf.Field('$1st')
#        fail(f'test_errors • #{e} FAIL', regression)
#    except uxf.Error as err:
#        ok += on_error(e, err, regression)
#
#    try:
#        total += 1
#        e = 180
#        _ = uxf.Table(records=(1, 2))
#        fail(f'test_errors • #{e} FAIL', regression)
#    except uxf.Error as err:
#        ok += on_error(e, err, regression)
#
#    try:
#        total += 1
#        e = 190
#        _ = uxf.Table(name='test', records=(1, 2))
#        fail(f'test_errors • #{e} FAIL', regression)
#    except uxf.Error as err:
#        ok += on_error(e, err, regression)

    if not regression:
        result = 'OK' if total == ok else 'FAIL'
        print(f'{ok}/{total} {result}')
    else:
        print(f'total={total} ok={ok}')


def on_error(code, err, regression):
    if not str(err).startswith(f'#{code}'):
        fail(f'test_errors • expected #{code} got, {err} FAIL', regression)
        return 0
    return 1


def fail(message, regression):
    if not regression:
        print(message)


if __name__ == '__main__':
    main()
