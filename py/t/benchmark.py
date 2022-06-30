#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import datetime
import os
import statistics
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
    print(f'load={load_t:.03f}s ', end='', flush=True)

    t = time.monotonic()
    for _ in range(scale):
        uxt2 = uxo1.dumps()
    dump_t = time.monotonic() - t

    total = load_t + dump_t
    print(f'dump={dump_t:0.03f}s (total={total:0.03f}s) ', end='')

    d = dict(drop_unused=True, replace_imports=True)
    uxo1 = uxf.loads(uxt1, **d)
    uxo2 = uxf.loads(uxt2, **d)
    if eq.eq(uxo1, uxo2):
        print('OK')
        record = (scale, load_t, dump_t, datetime.datetime.now())
        post_process_result(scale, record)
    else:
        print('uxo1 != uxo2') # we don't save bad results


def post_process_result(scale, record):
    filename = os.path.abspath('../py/t/benchmark.uxf.gz')
    try:
        uxo = uxf.load(filename)
    except uxf.Error:
        uxo = uxf.loads('''uxf 1.0 benchmark.py timings
=Result scale:int load:real dump:real when:datetime\n(Result)\n''')

    record = uxo.value.RecordClass(*record)
    load_times = []
    dump_times = []
    for result in uxo.value:
        if result.scale == scale:
            load_times.append(result.load)
            dump_times.append(result.dump)
    uxo.value.append(record)
    while len(uxo.value.records) > 2000:
        uxo.value.records.pop(0)
    uxo.dump(filename, format=uxf.Format(realdp=3))

    if load_times:
        load_mean = statistics.fmean(load_times)
        load_min = min(load_times)
        load_max = max(load_times)
        c = char_for(record.load, load_min, load_mean, load_max)
        print(f'load min={load_min:.03f}s mean={load_mean:.03f}s '
              f'max={load_max:.03f}s this={record.load:.03f}s {c}')
        dump_mean = statistics.fmean(dump_times)
        dump_min = min(dump_times)
        dump_max = max(dump_times)
        c = char_for(record.dump, dump_min, dump_mean, dump_max)
        print(f'dump min={dump_min:.03f}s mean={dump_mean:.03f}s '
              f'max={dump_max:.03f}s this={record.dump:.03f}s {c}')


def char_for(this, min, mean, max):
    if this < min:
        return '✔✔'
    if this < mean:
        return '✔'
    if this > max:
        return '✖✖'
    if this > mean:
        return '✖'
    return '~'



if __name__ == '__main__':
    main()
