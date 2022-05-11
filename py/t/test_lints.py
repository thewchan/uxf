#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import re
import subprocess
import sys
import tempfile

try:
    import os
    os.chdir(os.path.dirname(__file__)) # move to this file's dir
    sys.path.append('..')
    UXF_EXE = os.path.abspath('../uxf.py')
    os.chdir('../../testdata') # move to test data
finally:
    pass


def main():
    regression = False
    if len(sys.argv) > 1 and sys.argv[1] in {'-r', '--regression'}:
        regression = True
    total = ok = 0

    good_files = {name for name in os.listdir('.')
                  if os.path.isfile(name) and name.endswith(('.uxf',
                                                             '.uxf.gz'))}
    # TODO add more bad_files
    bad_files = set(_ERROR_FOR_FILENAME.keys())
    good_files -= bad_files
    good_files = sorted(good_files, key=by_number)
    bad_files = sorted(bad_files, key=by_number)
    for name in good_files:
        total += 1
        ok += check_good(name, regression)
    for name in bad_files:
        total += 1
        ok += check_bad(name, regression)
    if not regression:
        result = 'OK' if total == ok else 'FAIL'
        print(f'{ok}/{total} {result}')
    else:
        print(f'total={total} ok={ok}')


def check_good(name, regression):
    with tempfile.NamedTemporaryFile() as file:
        cmd = [UXF_EXE, name, '-v', file.name]
        reply = subprocess.run(cmd, capture_output=True, text=True)
    cmd = ' '.join(cmd)
    if reply.returncode != 0 or reply.stderr:
        if not regression:
            text = reply.stderr.strip()
            print(f'{cmd} • (good) FAIL got:\n{text!r}')
        return 0
    return 1


def check_bad(name, regression):
    with tempfile.NamedTemporaryFile() as file:
        cmd = [UXF_EXE, name, '-v', file.name]
    reply = subprocess.run(cmd, capture_output=True, text=True)
    cmd = ' '.join(cmd)
    if reply.returncode != 0:
        if not regression:
            print(f'{cmd} • (bad) FAIL terminated in error')
        return 0
    if not reply.stderr:
        if not regression:
            print(f'{cmd} • (bad) FAIL expected output not received')
        return 0
    actual = reply.stderr.strip()
    expected = _ERROR_FOR_FILENAME.get(name).strip()
    if expected is None:
        if actual == 'no errors found':
            return 1
        if not regression:
            print(f'{cmd} • (bad) FAIL expected nothing, got:\n{actual!r}')
        return 0
    if expected != actual:
        if not regression:
            print(f'{cmd} • (bad) FAIL expected {expected!r}, '
                  f'got\n{actual!r}')
        return 0
    return 1


def by_number(s):
    match = re.match(r'(?P<name>\D+)(?P<max_total>\d+)', s)
    if match is not None:
        return match['name'], int(match['max_total'])
    return s, 0


_ERROR_FOR_FILENAME = {
    't13.uxf': """
uxf.py:t13.uxf:43:#418:unused types: 'IPv4', 'IntPair', 'Playlists', \
'RGB', 'RGBA'""",
    't14.uxf': """
uxf.py:t14.uxf:39:#418:unused types: 'Categories', 'IPv4', 'IntPair', \
'Playlists', 'RGB', 'RGBA'""",
    't28.uxf': """
uxf.py:t28.uxf:39:#418:unused types: 'IPv4', 'IntPair', 'Playlists', \
'RGB', 'RGBA'""",
    't33.uxf': """
uxf.py:t33.uxf:10:#440:expected map, got <class 'uxf.Table'> Table \
None [] with 0 records #None""",
    't54.uxf': """
uxf.py:t54.uxf:4:#416:unused type: 'Pair'""",
    't55.uxf': """
uxf.py:t55.uxf:4:#416:unused type: 'Pair'""",
    't57.uxf': """
uxf.py:t57.uxf:14:#400:expected real, got <class 'str'> wrong
uxf.py:t57.uxf:20:#405:converted int to real""",
    'l56.uxf': """
uxf.py:l56.uxf:8:#492:converted str '2' to int
uxf.py:l56.uxf:8:#492:converted str '1983-04-07' to date
uxf.py:l56.uxf:10:#415:converted real to int
uxf.py:l56.uxf:14:#400:expected real, got <class 'str'> wrong
uxf.py:l56.uxf:17:#405:converted int to real
uxf.py:l56.uxf:19:#492:converted str '6.7' to real
uxf.py:l56.uxf:20:#492:converted str '9' to real
uxf.py:l56.uxf:21:#405:converted int to real
uxf.py:l56.uxf:22:#405:converted int to real
uxf.py:l56.uxf:23:#405:converted int to real
uxf.py:l56.uxf:24:#405:converted int to real
uxf.py:l56.uxf:24:#492:converted str '2008-09-01T23:59:46' to datetime
""",
    'l58.uxf': """
uxf.py:l58.uxf:13:#492:converted str 'yes' to bool
uxf.py:l58.uxf:13:#492:converted str 'no' to bool
uxf.py:l58.uxf:13:#492:converted str 't' to bool
uxf.py:l58.uxf:13:#492:converted str 'f' to bool
uxf.py:l58.uxf:13:#492:converted str 'true' to bool
uxf.py:l58.uxf:13:#492:converted str 'false' to bool
uxf.py:l58.uxf:13:#400:expected bool, got <class 'str'> duh
uxf.py:l58.uxf:14:#415:converted real to int
uxf.py:l58.uxf:14:#415:converted real to int
uxf.py:l58.uxf:14:#415:converted real to int
uxf.py:l58.uxf:14:#415:converted real to int
uxf.py:l58.uxf:14:#415:converted real to int
uxf.py:l58.uxf:15:#492:converted str '-1' to int
uxf.py:l58.uxf:15:#492:converted str '0' to int
uxf.py:l58.uxf:15:#492:converted str '1' to int
uxf.py:l58.uxf:16:#492:converted str '-0.1' to int
uxf.py:l58.uxf:16:#492:converted str '-1.0' to int
uxf.py:l58.uxf:16:#492:converted str '0.0' to int
uxf.py:l58.uxf:16:#492:converted str '0.1' to int
uxf.py:l58.uxf:16:#492:converted str '1.0' to int
uxf.py:l58.uxf:17:#400:expected int, got <class 'str'> one
uxf.py:l58.uxf:18:#405:converted int to real
uxf.py:l58.uxf:18:#405:converted int to real
uxf.py:l58.uxf:18:#405:converted int to real
uxf.py:l58.uxf:19:#492:converted str '-1' to real
uxf.py:l58.uxf:19:#492:converted str '0' to real
uxf.py:l58.uxf:19:#492:converted str '1' to real
uxf.py:l58.uxf:20:#492:converted str '-0.1' to real
uxf.py:l58.uxf:20:#492:converted str '-1.0' to real
uxf.py:l58.uxf:20:#492:converted str '0.0' to real
uxf.py:l58.uxf:20:#492:converted str '0.1' to real
uxf.py:l58.uxf:20:#492:converted str '1.0' to real
uxf.py:l58.uxf:21:#400:expected real, got <class 'str'> one
uxf.py:l58.uxf:23:#420:expected date, got <class 'int'> 1990
uxf.py:l58.uxf:23:#420:expected date, got <class 'float'> 1980.5
uxf.py:l58.uxf:23:#492:converted str '1906' to date
uxf.py:l58.uxf:23:#492:converted str '1907-05' to date
uxf.py:l58.uxf:23:#492:converted str '1909-08-18' to date
uxf.py:l58.uxf:25:#420:expected datetime, got <class 'int'> 1990
uxf.py:l58.uxf:25:#420:expected datetime, got <class 'float'> 1980.5
uxf.py:l58.uxf:25:#492:converted str '1906' to datetime
uxf.py:l58.uxf:25:#492:converted str '1907-05' to datetime
uxf.py:l58.uxf:25:#492:converted str '1909-08-18' to datetime
uxf.py:l58.uxf:26:#492:converted str '1911-11-13T04' to datetime
uxf.py:l58.uxf:26:#492:converted str '1913-12-01T05:19' to datetime
uxf.py:l58.uxf:29:#420:expected str, got <class 'int'> 3
uxf.py:l58.uxf:29:#420:expected str, got <class 'int'> 4
uxf.py:l58.uxf:29:#420:expected str, got <class 'float'> 5.6
uxf.py:l58.uxf:29:#420:expected str, got <class 'float'> -7.9
uxf.py:l58.uxf:29:#420:expected str, got <class 'int'> -8
uxf.py:l58.uxf:29:#420:expected str, got <class 'datetime.date'> \
1990-01-11
uxf.py:l58.uxf:29:#420:expected str, got <class 'datetime.datetime'> \
1995-03-15 22:30:00
uxf.py:l58.uxf:30:#420:expected str, got <class 'datetime.datetime'> \
1998-10-17 20:18:45
uxf.py:l58.uxf:31:#420:expected str, got <class 'bytes'> b'UXF 1.0'
uxf.py:l58.uxf:32:#400:expected int, got <class 'str'> one
uxf.py:l58.uxf:32:#400:expected int, got <class 'str'> two
uxf.py:l58.uxf:34:#415:converted real to int
uxf.py:l58.uxf:34:#415:converted real to int
uxf.py:l58.uxf:34:#420:expected int, got <class 'datetime.date'> \
1990-01-11
uxf.py:l58.uxf:35:#420:expected int, got <class 'datetime.datetime'> \
1995-03-15 22:30:00
uxf.py:l58.uxf:35:#420:expected int, got <class 'datetime.datetime'> \
1998-10-17 20:18:45
uxf.py:l58.uxf:36:#420:expected int, got <class 'bytes'> b'UXF 1.0'
uxf.py:l58.uxf:36:#440:expected int, got <class 'uxf.Table'> Table \
None [] with 0 records #None
uxf.py:l58.uxf:36:#400:expected int, got <class 'str'> a
uxf.py:l58.uxf:36:#400:expected int, got <class 'str'> b
uxf.py:l58.uxf:38:#416:unused type: 'by'""",
    'l59.uxf': """
uxf.py:l59.uxf:20:#418:unused types: 'one', 'three', 'two'""",
    }


if __name__ == '__main__':
    main()
