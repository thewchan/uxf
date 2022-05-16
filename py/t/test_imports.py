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

    errors = []

    def on_error(lino, code, message, *, filename, fail=False,
                 verbose=True):
        errors.append((lino, code, message, filename, fail, verbose))

    actual_uxo = uxf.load('t63.uxf', on_error=on_error)
    expected_uxo = uxf.loads(EXPECTED_UXT, on_error=lambda *_a, **_k: None)
    for ((attype, atclass), (ettype, etclass)) in zip(
            actual_uxo.tclasses.items(), expected_uxo.tclasses.items()):
        total += 1
        if attype == ettype:
            ok += 1
        total += 1
        if eq.eq(atclass, etclass):
            ok += 1
    total += 1
    if actual_uxo.imports == EXPECTED_IMPORTS:
        ok += 1
    total += 1
    if errors == [(12, 416, "unused type: 'dob'", 't63.uxf', False, True)]:
        ok += 1
    if not regression:
        result = 'OK' if total == ok else 'FAIL'
        print(f'{ok}/{total} {result}')
    else:
        print(f'total={total} ok={ok}')


EXPECTED_UXT = '''uxf 1.0
= Slide title body
= #<title> h1 content
= #<subtitle> h2 content
= #<bullet item> B content
= #<para> p content
= #<image> img content image:bytes
= #<monospace inline> m content
= #<monospace block> pre content
= #<italic> i content
= url content link
= #<newline with no content> nl empty
= IPv4 A:int B:int C:int D:int
= #<0-255 per component> rgb red:int green:int blue:int
= #<0-255 per component> rgba red:int green:int blue:int alpha:int
= #<a pair of any two values> pair first second
=cmyk cyan:real magenta:real yellow:real black:real
=point2d x:int y:int
[]
'''

EXPECTED_IMPORTS = {
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


if __name__ == '__main__':
    main()
