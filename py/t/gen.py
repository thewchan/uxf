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
    scale = 7 # Approx 1 MB
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


def generate(*, scale=7):
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
    text1 = text[i:j + 1]
    for table in uxo.value:
        table.records.reverse()
    text = uxo.dumps()
    i = text.find('[')
    j = text.rfind(']')
    text2 = text[i:j + 1]
    n = 1
    uxt.append(f'{{<Music #{n}>')
    uxt.append(random.choice((text1, text2)))
    uxt.append('<Color values> [')
    scale3 = scale ** 3
    for _ in range(random.randrange(scale3 - 19, scale3 + 19)):
        r = random.randrange(0, 256)
        g = random.randrange(0, 256)
        b = random.randrange(0, 256)
        a = random.randrange(0, 256)
        uxt.append(f'    (rgba {r} {g} {b} {a})')
    uxt.append(']')
    if n < scale:
        uxt.append(f'<Music #{n + 1}> ')
        uxt.append(random.choice((text1, text2)))
        n += 1
    uxt.append('<Fractions> [')
    scale2 = scale ** 2
    for _ in range(random.randrange(scale2 - 3, scale2 + 3)):
        a = random.randrange(0, 1000000 + scale3)
        b = random.randrange(1, 1000000 + scale3)
        uxt.append(f'    (Fraction {a} {b})')
    uxt.append(']')
    if n < scale:
        uxt.append(f'<Music #{n + 1}> ')
        uxt.append(random.choice((text1, text2)))
        n += 1
    uxt.append('<Complex numbers> [')
    for _ in range(random.randrange(scale2 - 3, scale2 + 3)):
        r = random.random() * (1000000 + scale3)
        i = random.random() * (1000000 + scale3)
        uxt.append(f'    (Complex {r} {i})')
    uxt.append(']')
    if n < scale:
        uxt.append(f'<Music #{n + 1}> ')
        uxt.append(random.choice((text1, text2)))
        n += 1
    uxt.append('<3D Points> [')
    for _ in range(random.randrange(scale3 - 19, scale3 + 19)):
        x1 = random.randrange(-9999, 10000)
        y1 = random.randrange(-9999, 10000)
        z1 = random.randrange(-9999, 10000)
        x2 = random.randrange(-9999, 10000)
        y2 = random.randrange(-9999, 10000)
        z2 = random.randrange(-9999, 10000)
        x3 = random.randrange(-9999, 10000)
        y3 = random.randrange(-9999, 10000)
        z3 = random.randrange(-9999, 10000)
        uxt.append(
            f'    (point3d {x1} {y1} {z1} {x2} {y2} {z2} {x3} {y3} {z3})')
    uxt.append(']')
    while n < scale:
        uxt.append(f'<Music #{n + 1}> ')
        uxt.append(random.choice((text1, text2)))
        n += 1
    uxt.append('\n}')
    return '\n'.join(uxt)


if __name__ == '__main__':
    main()
