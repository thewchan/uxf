#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
Generates a mock UXF files in memory or on disk for benchmarking purposes.
'''

import os
import random
import sys
import tempfile

try:
    PATH = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(os.path.join(PATH, '../')))
    import uxf
    os.chdir(os.path.join(PATH, '../../testdata')) # move to test data
finally:
    pass


def main():
    scale = 7 # Approx 1MB
    if len(sys.argv) > 1:
        if sys.argv[1] in {'-h', '--help'}:
            raise SystemExit(
                'usage: gen.py [scale]\ndefault scale is 7 → ~1MB')
        scale = int(sys.argv[1])
    uxt = generate(scale=scale)
    with tempfile.NamedTemporaryFile('wt', encoding='utf-8', prefix='gen-',
                                     suffix='.uxf', delete=False) as file:
        n = file.write(uxt)
        name = file.name
    print(f'wrote {name} of {n:,} bytes')


def generate(*, scale=7, seed=104297):
    random.seed(seed)
    uxt = ['uxf 1.0']
    imports = ['!fraction', '! complex']
    random.shuffle(imports)
    uxt += imports
    ttypes = ['=rgba red:int green:int blue:int alpha:int',
              '=point3d x:int y:int z:int',
              '= Categories CID:int Title:str Selected:bool',
              '= Playlists PID:int Title:str CID:int Selected:bool',
              '= Tracks TID Title Seconds Filename Selected PID']
    random.shuffle(ttypes)
    uxt += ttypes
    uxo = uxf.load('t5.uxf')
    text = uxo.dumps()
    i = text.find('[')
    j = text.rfind(']')
    for _ in range(scale):
        uxt.append(text[i:j])
    uxt.append('{<Color values> [')
    for _ in range(scale ** 3):
        r = random.randrange(0, 256)
        g = random.randrange(0, 256)
        b = random.randrange(0, 256)
        a = random.randrange(0, 256)
        uxt.append(f'    (rgba {r} {g} {b} {a})')
    uxt.append(']')
    uxt.append('<Fractions> [')
    for _ in range(scale ** 2):
        a = random.randrange(0, 1000000)
        b = random.randrange(1, 1000000)
        uxt.append(f'    (Fraction {a} {b})')
    uxt.append(']')
    uxt.append('<Complex numbers> [')
    for _ in range(scale ** 2):
        r = random.random() * 1000000
        i = random.random() * 1000000
        uxt.append(f'    (Complex {r} {i})')
    uxt.append(']')
    uxt.append('<3D Points> [')
    for _ in range(scale ** 3):
        x1 = random.randrange(-1000, 1000)
        y1 = random.randrange(-1000, 1000)
        z1 = random.randrange(-1000, 1000)
        x2 = random.randrange(-1000, 1000)
        y2 = random.randrange(-1000, 1000)
        z2 = random.randrange(-1000, 1000)
        x3 = random.randrange(-1000, 1000)
        y3 = random.randrange(-1000, 1000)
        z3 = random.randrange(-1000, 1000)
        uxt.append(
            f'    (point3d {x1} {y1} {z1} {x2} {y2} {z2} {x3} {y3} {z3})')
    uxt.append(']\n}')
    uxt.append(']\n')
    return '\n'.join(uxt)


if __name__ == '__main__':
    main()
