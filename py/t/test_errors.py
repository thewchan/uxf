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
        e = 170
        uxf.loads('uxf 1.0\n[1 2 5_invalid]', warn_is_error=True)
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

    try:
        total += 1
        e = 200
        uxf.loads('uxf 1.0\n[(:AB CD EF GH:)]', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 210
        uxf.loads('uxf 1.0\n[-7F]', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 220
        uxf.loads('uxf 1.0\n[7.8.9]', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 220
        uxf.loads('uxf 1.0\n[2020-02-20T20e20]', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 231
        uxf.loads('uxf 1.0\n[2020-02-20T20:20:20-07:31T]',
                  warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    # TODO how to trigger 240?
    # TODO how to trigger 250?
    # TODO how to trigger 260?

    try:
        total += 1
        e = 270
        uxf.loads('uxf 1.0\n[(:AB 12:]', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 280
        uxf.loads('uxf 1.0\n=p q\n{(p 1) 8}', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 290
        uxf.loads('uxf 1.0\n{7.9 8}', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    table = uxf.Table(name='Pair', fields=('first', 'second'))
    uxo = uxf.Uxf({})
    uxo.data.append('key')
    uxo.data.append('value')

    try:
        total += 1
        e = 280
        uxo.data.append(table)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 290
        uxo.data.append(3.8)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 300
        _ = uxf.Field('1st')
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 310
        _ = uxf.Field('$1st')
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 320
        _ = uxf.Table(records=(1, 2))
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 330
        _ = uxf.Table(name='test', records=(1, 2))
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

# TODO 340

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
