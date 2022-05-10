#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import collections
import sys


# TODO how to trigger 240?
# TODO how to trigger 250?
# TODO how to trigger 260?
# TODO how to trigger 340?
# TODO how to trigger 360?
# TODO how to trigger 370?
# TODO how to trigger 380?
# TODO how to trigger 390?
# TODO how to trigger 410?
# TODO how to trigger 420?
# TODO how to trigger 490?
# TODO how to trigger 500?
# TODO how to trigger 510?
# TODO how to trigger 530?
# TODO how to trigger 540?
# TODO how to trigger 550?


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

    try:
        total += 1
        e = 298
        _ = uxf.Table(name='', records=(1, 2))
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

    try:
        total += 1
        e = 350
        t = uxf.Table(name='t1')
        t.append(1)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 350
        t = uxf.Table(name='t1', fields=('a', 'b'))
        t.ttype.fields = None
        t.append(1)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 400
        uxf.loads('uxf 1.0\n(:AB:)', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 190
        uxf.loads('uxf 1.0\n{1 2 #<3> 4}', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 430
        uxf.loads('uxf 1.0\n{int p}', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 440
        uxf.loads('uxf 1.0\n[q]', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 450
        uxf.loads('uxf 1.0\n(r)', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 460
        uxf.loads('uxf 1.0\n{p}', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 470
        uxf.loads('uxf 1.0\n[int real]', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 480
        uxf.loads('uxf 1.0\n{int real str}', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 512
        uxo = uxf.loads('uxf 1.0\n[1 2 3}', warn_is_error=True)
        print(uxo.dumps())
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 520
        uxf.loads('uxf 1.0\nint', warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 561
        uxo = uxf.Uxf()
        uxo.data = [3+2j] # noqa: E226
        _ = uxo.dumps(warn_is_error=True)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

    try:
        total += 1
        e = 570
        uxf.add_converter(str)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += on_error(e, err, regression)

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
