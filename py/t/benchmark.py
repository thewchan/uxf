#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import datetime
import os
import sys
import time

try:
    PATH = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(os.path.join(PATH, '../')))
    import uxf
    sys.path.append(os.path.abspath(os.path.join(PATH, '../t/')))
    import eq
    import gen
    os.chdir(os.path.join(PATH, '../../testdata')) # move to testdata
finally:
    pass


def main():
    scale = 7
    if len(sys.argv) > 1:
        if sys.argv[1] in {'-h', '--help'}:
            raise SystemExit(
                'usage: benchmark.py [scale] default scale is 7 → ~1MB')
        else:
            scale = int(sys.argv[1])
    print(f'scale={scale} ', end='', flush=True)

    uxt1 = gen.generate(scale=scale)

    t = time.monotonic()
    for _ in range(scale):
        uxo1 = uxf.loads(uxt1)
    load_t = time.monotonic() - t
    print(f'load={load_t:.03f}sec ', end='', flush=True)

    t = time.monotonic()
    for _ in range(scale):
        uxt2 = uxo1.dumps()
    dump_t = time.monotonic() - t

    total = load_t + dump_t
    print(f'dump={dump_t:0.03f}sec (total={total:0.03f}sec) ', end='')

    d = dict(drop_unused=True, replace_imports=True)
    uxo1 = uxf.loads(uxt1, **d)
    uxo2 = uxf.loads(uxt2, **d)
    if eq.eq(uxo1, uxo2):
        ok = True
        print('OK')
    else:
        ok = False
        print('uxo1 != uxo2')

    filename = os.path.abspath('../py/t/benchmark.uxf.gz')
    try:
        uxo = uxf.load(filename)
    except uxf.Error:
        uxo = uxf.loads('''uxf 1.0 benchmark.py timings
=Result scale:int load:real dump:real when:datetime ok:bool\n(Result)\n''')

    record = (scale, load_t, dump_t, datetime.datetime.now(), ok)
    comparable = []
    for result in uxo.value:
        if result.scale == scale:
            comparable.append(result)
    if comparable:
        print('TODO compare with prev results')
    uxo.value.append(record)
    while len(uxo.value.records) > 2000:
        uxo.value.records.pop(0)
    uxo.dump(filename, format=uxf.Format(realdp=3))


if __name__ == '__main__':
    main()
