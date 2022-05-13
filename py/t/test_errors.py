#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import sys
import os


try:
    PATH = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(os.path.join(PATH, '../')))
    import uxf
    os.chdir(os.path.join(PATH, '../../testdata')) # move to test data
finally:
    pass


def on_error(lino, code, message, *, filename='-', fail=True,
             verbose=False):
    raise uxf.Error(f'uxf.py:{filename}:{lino}:#{code}:{message}')


def main():
    regression = False
    if len(sys.argv) > 1 and sys.argv[1] in {'-r', '--regression'}:
        regression = True
    total = ok = 0

    try:
        total += 1
        e = 110
        uxf.loads('not a uxf file', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 120
        uxf.loads('uxf\n', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 130
        uxf.loads('UXF 1.0\n', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 141
        uxf.loads('uxf 9.0\n', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 151
        uxf.loads('uxf 1.0x\n', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 160
        uxf.loads('uxf 1.0\n# Not a comment', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 170
        uxf.loads('uxf 1.0\n* invalid', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 170
        uxf.loads('uxf 1.0\n[1 2 5_invalid]', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 180
        uxf.loads('uxf 1.0\n[# 123]', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 190
        uxf.loads('uxf 1.0\n[123 #<comment>]', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 190
        uxf.loads('uxf 1.0\n{1 2 #<3> 4}', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 200
        uxf.loads('uxf 1.0\n[(:AB CD EF GH:)]', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 220
        uxf.loads('uxf 1.0\n[7.8.9]', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 220
        uxf.loads('uxf 1.0\n[2020-02-20T20e20]', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 231
        uxf.loads('uxf 1.0\n[2020-02-20T20:20:20-07:31T]',
                  on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 270
        uxf.loads('uxf 1.0\n[(:AB 12:]', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 280
        uxf.loads('uxf 1.0\n=p q\n{(p 1) 8}', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    table = uxf.Table(ttype='Pair', fields=('first', 'second'))
    uxo = uxf.Uxf({})
    uxo.data.append('key')
    uxo.data.append('value')

    try:
        total += 1
        e = 280
        uxo.data.append(table)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 290
        uxf.loads('uxf 1.0\n{7.9 8}', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 290
        uxo.data.append(3.8)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 298
        _ = uxf.Table(ttype='', records=(1, 2))
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 300
        _ = uxf.Field('1st')
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 310
        _ = uxf.Field('$1st')
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 320
        _ = uxf.Table(records=(1, 2))
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 330
        _ = uxf.Table(ttype='test', records=(1, 2))
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 330
        _ = uxf.Table(ttype='test', records=(1, 2))
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 350
        t = uxf.Table(ttype='t1')
        t.append(1)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 350
        t = uxf.Table(ttype='t1', fields=('a', 'b'))
        t.tclass.fields = None
        t.append(1)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 460
        uxf.loads('uxf 1.0\n[-7F]', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 460
        uxf.loads('uxf 1.0\n{p}', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 400
        uxf.loads('uxf 1.0\n(:AB:)', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 430
        uxf.loads('uxf 1.0\n{int p}', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 440
        uxf.loads('uxf 1.0\n[q]', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 450
        uxf.loads('uxf 1.0\n(r)', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 456
        uxf.loads('''uxf 1.0
=p x:int y:int
=q a:real b:real
{str p
  <one> (#<ok> p 1 2 -3 4 5 6)
  <four> (#<wrong> q 8.1 -9.3)
  <five> (#<ok2> p -7 -6)
}''', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 470
        uxf.loads('uxf 1.0\n[int real]', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 480
        uxf.loads('uxf 1.0\n{int real str}', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 492
        uxf.loads('''uxf 1.0
=p x:int y:int
{str p <one> (#<ok> p 1 2 -3 4 5 6)
<three> (#<worse> p 11 -12 <-1> <13>)''', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 498
        uxf.loads('''uxf 1.0
=p x:int y:int
{str p <one> (#<ok> p 1 2 -3 4 5 6)
<two> (#<bad> p 7 -8 9.0 10)}''', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 498
        uxf.loads('''uxf 1.0
=p x:int y:int
{str p <one> (#<ok> p 1 2 -3 4 5 6)
<two> (#<bad> p 7 -8 9.0 10)}''', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 512
        uxo = uxf.loads('uxf 1.0\n[1 2 3}', on_error=on_error)
        print(uxo.dumps(on_error=on_error))
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 520
        uxf.loads('uxf 1.0\nint', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 561
        uxo = uxf.Uxf()
        uxo.data = [3+2j] # noqa: E226
        _ = uxo.dumps(on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try:
        total += 1
        e = 570
        uxf.add_converter(str)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    if not regression:
        result = 'OK' if total == ok else 'FAIL'
        print(f'{ok}/{total} {result}')
    else:
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
