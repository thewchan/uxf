#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import os
import sys

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
    total = ok = 0

    # good mixed imports
    filename = 't63.uxf'
    total += 1
    actual_uxo = uxf.Uxf()
    try:
        actual_uxo = uxf.load(filename, on_error=on_error)
        ok += 1
    except uxf.Error as err:
        if not regression:
            print(err)
    total += 1
    try:
        expected_uxo = uxf.loads(EXPECTED_UXT63,
                                 on_error=lambda *_a, **_k: None)
        ok += 1
    except uxf.Error as err:
        if not regression:
            print(err)
    total, ok = test(total, ok, actual_uxo, expected_uxo,
                     EXPECTED_IMPORTS63, filename, regression)

    try: # attempt to import itself
        total += 1
        e = 176
        actual_uxo = uxf.load('i64.uxi', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try: # attempt to do circular import #1
        total += 1
        e = 580
        actual_uxo = uxf.load('i65.uxi', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    try: # attempt to do circular import #2
        total += 1
        e = 580
        actual_uxo = uxf.load('i66.uxi', on_error=on_error)
        fail(f'test_errors • #{e} FAIL', regression)
    except uxf.Error as err:
        ok += got_error(e, err, regression)

    # good but dumplicate imports
    filename = 'i67.uxi'
    try:
        actual_uxo = uxf.load(filename, on_error=on_error)
        ok += 1
    except uxf.Error as err:
        if not regression:
            print(err)
    try:
        expected_uxo = uxf.loads(EXPECTED_UXT63,
                                 on_error=lambda *_a, **_k: None)
        ok += 1
    except uxf.Error as err:
        if not regression:
            print(err)
    total, ok = test(total, ok, actual_uxo, expected_uxo,
                     EXPECTED_IMPORTS67, filename, regression)

    total += 1
    if on_error.errors == EXPECTED_ERRORS:
        ok += 1
    elif not regression:
        for err in on_error.errors:
            print(err)

    if not regression:
        result = 'OK' if total == ok else 'FAIL'
        print(f'{ok}/{total} {result}')
    else:
        print(f'total={total} ok={ok}')


def test(total, ok, actual_uxo, expected_uxo, expected_imports, filename,
         regression):
    for ((attype, atclass), (ettype, etclass)) in zip(
            actual_uxo.tclasses.items(), expected_uxo.tclasses.items()):
        total += 1
        if attype == ettype:
            ok += 1
        elif not regression:
            print(f'{filename} ttype {attype} != {ettype}')
        total += 1
        if eq.eq(atclass, etclass, ignore_comments=True):
            ok += 1
        elif not regression:
            print(f'{filename} ttype {atclass} != {etclass}')
    total += 1
    if actual_uxo.imports == expected_imports:
        ok += 1
    elif not regression:
        print(f'{filename} imports {sorted(actual_uxo.imports)} '
              f'!= {expected_imports}')
    return total, ok


def on_error(lino, code, message, *, filename, fail=False, verbose=True):
    text = f'uxf.py:{filename}:{lino}:#{code}:{message}'
    on_error.errors.append(text)
    if fail:
        raise uxf.Error(text)
on_error.errors = [] # noqa: E305


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


EXPECTED_UXT63 = '''uxf 1.0
=Slide title body
=h1 content
=h2 content
=B content
=p content
=img content image:bytes
=m content
=pre content
=i content
=url content link
=nl empty
=IPv4 A:int B:int C:int D:int
=rgb red:int green:int blue:int
=rgba red:int green:int blue:int alpha:int
=pair first second
=cmyk cyan:real magenta:real yellow:real black:real
=point2d x:int y:int
[]
'''

EXPECTED_IMPORTS63 = {
    'Slide': 'http://www.qtrac.eu/ttype-eg.uxf',
    'h1': 'http://www.qtrac.eu/ttype-eg.uxf',
    'h2': 'http://www.qtrac.eu/ttype-eg.uxf',
    'B': 'http://www.qtrac.eu/ttype-eg.uxf',
    'p': 'http://www.qtrac.eu/ttype-eg.uxf',
    'img': 'http://www.qtrac.eu/ttype-eg.uxf',
    'm': 'http://www.qtrac.eu/ttype-eg.uxf',
    'pre': 'http://www.qtrac.eu/ttype-eg.uxf',
    'i': 'http://www.qtrac.eu/ttype-eg.uxf',
    'url': 'http://www.qtrac.eu/ttype-eg.uxf',
    'nl': 'http://www.qtrac.eu/ttype-eg.uxf',
    'IPv4': 'ttype-test',
    'rgb': 'ttype-test',
    'rgba': 'ttype-test',
    'pair': 'ttype-test',
    'cmyk': 't63.uxt',
    'point2d': 't63.uxt'}

EXPECTED_IMPORTS67 = {
    'Slide': 'http://www.qtrac.eu/ttype-eg.uxf',
    'h1': 'http://www.qtrac.eu/ttype-eg.uxf',
    'h2': 'http://www.qtrac.eu/ttype-eg.uxf',
    'B': 'http://www.qtrac.eu/ttype-eg.uxf',
    'p': 'http://www.qtrac.eu/ttype-eg.uxf',
    'img': 'http://www.qtrac.eu/ttype-eg.uxf',
    'm': 'http://www.qtrac.eu/ttype-eg.uxf',
    'pre': 'http://www.qtrac.eu/ttype-eg.uxf',
    'i': 'http://www.qtrac.eu/ttype-eg.uxf',
    'url': 'http://www.qtrac.eu/ttype-eg.uxf',
    'nl': 'http://www.qtrac.eu/ttype-eg.uxf',
    'IPv4': 'ttype-test',
    'rgb': 'ttype-test',
    'rgba': 'ttype-test',
    'pair': 'ttype-test',
    'cmyk': 't63.uxt',
    'point2d': 't63.uxt'}

EXPECTED_ERRORS = [
    "uxf.py:t63.uxf:12:#422:unused ttype: 'dob'",
    "uxf.py:i64.uxi:1:#176:a UXF file cannot import itself",
    "uxf.py:i66.uxi:4:#450:expected table ttype, got 4:IDENTIFIER='img'",
    "uxf.py:i65.uxi:1:#580:cannot do circular imports "
    "'/home/mark/app/uxf/testdata/i66.uxi'",
    "uxf.py:i65.uxi:4:#450:expected table ttype, got 4:IDENTIFIER='img'",
    "uxf.py:i66.uxi:1:#580:cannot do circular imports "
    "'/home/mark/app/uxf/testdata/i65.uxi'",
    "uxf.py:i67.uxi:11:#422:unused ttype: 'dob'"]


if __name__ == '__main__':
    main()
