#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

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
    magnitude = 7
    if len(sys.argv) > 1:
        if sys.argv[1] in {'-h', '--help'}:
            raise SystemExit('''usage: benchmark.py [magnitude]
default magnitude is 7 → ~1MB''')
        else:
            magnitude = int(sys.argv[1])
    print(f'magnitude={magnitude} ', end='', flush=True)

    uxt1 = gen.generate(magnitude=magnitude)

    t = time.monotonic()
    for _ in range(magnitude):
        uxo1 = uxf.loads(uxt1)
    load_t = time.monotonic() - t
    print(f'load={load_t:.03f}sec ', end='', flush=True)

    t = time.monotonic()
    for _ in range(magnitude):
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
        uxo = uxf.loads('''uxf 1.0
=result magnitude:int load:real dump:real ok:bool\n(result)\n''')

    record = (magnitude, load_t, dump_t, ok)
    comparable = []
    for result in uxo.value:
        if result.magnitude == magnitude:
            comparable.append(result)
    if comparable:
        print('TODO compare with prev results')
    uxo.value.append(record)
    uxo.dump(filename)


if __name__ == '__main__':
    main()
