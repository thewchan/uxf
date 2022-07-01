#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import datetime
import math
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

    uxt1s = []
    for _ in range(scale):
        uxt1s.append(gen.generate(scale=scale))
    mean_bytes = round(statistics.fmean(len(x.encode()) for x in uxt1s) //
                       1000)
    print(f'~{mean_bytes:,} KB ', end='', flush=True)
    mean_lines = round(statistics.fmean(len(x.splitlines()) for x in uxt1s))
    print(f'~{mean_lines:,} lines ', end='', flush=True)

    t = time.monotonic()
    uxos = []
    for uxt1 in uxt1s:
        uxos.append(uxf.loads(uxt1))
    load_t = time.monotonic() - t
    print(f'load={load_t:.03f}s ', end='', flush=True)

    t = time.monotonic()
    uxt2s = []
    for uxo in uxos:
        uxt2s.append(uxo.dumps())
    dump_t = time.monotonic() - t

    total = load_t + dump_t
    print(f'dump={dump_t:0.03f}s (total={total:0.03f}s', end='')

    d = dict(drop_unused=True, replace_imports=True)
    ok = 0
    for i in range(scale):
        uxo1 = uxf.loads(uxt1s[i], **d)
        uxo2 = uxf.loads(uxt2s[i], **d)
        if eq.eq(uxo1, uxo2):
            ok += 1
    if ok == scale:
        filename, uxo = get_timings()
        print(f' timings={len(uxo.value):,}) OK')
        record = (scale, load_t, dump_t, datetime.datetime.now())
        post_process_result(filename, uxo, scale, record)
    else:
        print(') uxo1 != uxo2') # we don't save bad results


def get_timings():
    filename = os.path.abspath('../py/t/benchmark.uxf.gz')
    try:
        return filename, uxf.load(filename)
    except uxf.Error:
        return filename, uxf.loads('''uxf 1.0 benchmark.py timings
=Result scale:int load:real dump:real when:datetime\n(Result)\n''')


def post_process_result(filename, uxo, scale, record):
    load_times = []
    dump_times = []
    for result in uxo.value:
        if result.scale == scale:
            load_times.append(result.load)
            dump_times.append(result.dump)
    uxo.value.append(record) # in as a tuple
    record = uxo.value.last  # out as an editabletuple
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
    if math.isclose(this, mean):
        return '='
    return '~'



if __name__ == '__main__':
    main()
