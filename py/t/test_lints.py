#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import re
import subprocess
import sys

try:
    import os
    os.chdir(os.path.dirname(__file__)) # move to this file's dir
    sys.path.append('..')
    UXFLINT_EXE = os.path.abspath('../uxflint.py')
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
    cmd = [UXFLINT_EXE, name]
    reply = subprocess.run(cmd, capture_output=True, text=True)
    cmd = ' '.join(cmd)
    if reply.returncode != 0 or reply.stdout or reply.stderr:
        if reply.stdout.strip() == 'no errors found':
            return 1
        if not regression:
            text = reply.stdout
            if text:
                text += '\n' + reply.stderr
            text = text.strip()
            print(f'{cmd} • (good) FAIL got:\n{text!r}')
        return 0
    return 1


def check_bad(name, regression):
    cmd = [UXFLINT_EXE, name]
    reply = subprocess.run(cmd, capture_output=True, text=True)
    cmd = ' '.join(cmd)
    if reply.returncode != 0:
        if not regression:
            print(f'{cmd} • (bad) FAIL terminated in error')
        return 0
    if not reply.stdout:
        if not regression:
            print(f'{cmd} • (bad) FAIL expected output not received')
        return 0
    actual = reply.stdout.strip()
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
    't13.uxf': '''
uxflint.py:t13.uxf:43:#530:unused types: 'IPv4', 'IntPair', 'Playlists', \
'RGB', 'RGBA'
could have found one error but could not fix it''',
    't14.uxf': '''
uxflint.py:t14.uxf:39:#530:unused types: 'Categories', 'IPv4', 'IntPair', \
'Playlists', 'RGB', 'RGBA'
could have found one error but could not fix it''',
    't28.uxf': '''
uxflint.py:t28.uxf:39:#530:unused types: 'IPv4', 'IntPair', 'Playlists', \
'RGB', 'RGBA'
could have found one error but could not fix it''',
    't33.uxf': '''
uxflint.py:t33.uxf:10:#492:expected map, got <class 'uxf.Table'> Table \
None [] with 0 records #None
could have found one error but could not fix it''',
    't54.uxf': '''
uxflint.py:t54.uxf:4:#520:unused type: 'Pair'
could have found one error but could not fix it''',
    't55.uxf': '''
uxflint.py:t55.uxf:4:#520:unused type: 'Pair'
could have found one error but could not fix it''',
    't57.uxf': '''
uxflint.py:t57.uxf:14:#484:expected real, got <class 'str'> wrong
uxflint.py:t57.uxf:20:#487:converted int to real
could have found 2 errors and fixed one of them''',
    'l56.uxf': '''
uxflint.py:l56.uxf:8:#485:converted str '2' to int
uxflint.py:l56.uxf:8:#485:converted str '1983-04-07' to date
uxflint.py:l56.uxf:10:#489:converted real to int
uxflint.py:l56.uxf:14:#484:expected real, got <class 'str'> wrong
uxflint.py:l56.uxf:17:#487:converted int to real
uxflint.py:l56.uxf:19:#485:converted str '6.7' to real
uxflint.py:l56.uxf:20:#485:converted str '9' to real
uxflint.py:l56.uxf:21:#487:converted int to real
uxflint.py:l56.uxf:22:#487:converted int to real
uxflint.py:l56.uxf:23:#487:converted int to real
uxflint.py:l56.uxf:24:#487:converted int to real
uxflint.py:l56.uxf:24:#485:converted str '2008-09-01T23:59:46' to datetime
could have found 12 errors and fixed 11 of them''',
    'l58.uxf': '''
uxflint.py:l58.uxf:13:#485:converted str 'yes' to bool
uxflint.py:l58.uxf:13:#485:converted str 'no' to bool
uxflint.py:l58.uxf:13:#485:converted str 't' to bool
uxflint.py:l58.uxf:13:#485:converted str 'f' to bool
uxflint.py:l58.uxf:13:#485:converted str 'true' to bool
uxflint.py:l58.uxf:13:#485:converted str 'false' to bool
uxflint.py:l58.uxf:13:#484:expected bool, got <class 'str'> duh
uxflint.py:l58.uxf:14:#489:converted real to int
uxflint.py:l58.uxf:14:#489:converted real to int
uxflint.py:l58.uxf:14:#489:converted real to int
uxflint.py:l58.uxf:14:#489:converted real to int
uxflint.py:l58.uxf:14:#489:converted real to int
uxflint.py:l58.uxf:15:#485:converted str '-1' to int
uxflint.py:l58.uxf:15:#485:converted str '0' to int
uxflint.py:l58.uxf:15:#485:converted str '1' to int
uxflint.py:l58.uxf:16:#485:converted str '-0.1' to int
uxflint.py:l58.uxf:16:#485:converted str '-1.0' to int
uxflint.py:l58.uxf:16:#485:converted str '0.0' to int
uxflint.py:l58.uxf:16:#485:converted str '0.1' to int
uxflint.py:l58.uxf:16:#485:converted str '1.0' to int
uxflint.py:l58.uxf:17:#484:expected int, got <class 'str'> one
uxflint.py:l58.uxf:18:#487:converted int to real
uxflint.py:l58.uxf:18:#487:converted int to real
uxflint.py:l58.uxf:18:#487:converted int to real
uxflint.py:l58.uxf:19:#485:converted str '-1' to real
uxflint.py:l58.uxf:19:#485:converted str '0' to real
uxflint.py:l58.uxf:19:#485:converted str '1' to real
uxflint.py:l58.uxf:20:#485:converted str '-0.1' to real
uxflint.py:l58.uxf:20:#485:converted str '-1.0' to real
uxflint.py:l58.uxf:20:#485:converted str '0.0' to real
uxflint.py:l58.uxf:20:#485:converted str '0.1' to real
uxflint.py:l58.uxf:20:#485:converted str '1.0' to real
uxflint.py:l58.uxf:21:#484:expected real, got <class 'str'> one
uxflint.py:l58.uxf:23:#488:expected date, got <class 'int'> 1990
uxflint.py:l58.uxf:23:#488:expected date, got <class 'float'> 1980.5
uxflint.py:l58.uxf:23:#485:converted str '1906' to date
uxflint.py:l58.uxf:23:#485:converted str '1907-05' to date
uxflint.py:l58.uxf:23:#485:converted str '1909-08-18' to date
uxflint.py:l58.uxf:25:#488:expected datetime, got <class 'int'> 1990
uxflint.py:l58.uxf:25:#488:expected datetime, got <class 'float'> 1980.5
uxflint.py:l58.uxf:25:#485:converted str '1906' to datetime
uxflint.py:l58.uxf:25:#485:converted str '1907-05' to datetime
uxflint.py:l58.uxf:25:#485:converted str '1909-08-18' to datetime
uxflint.py:l58.uxf:26:#485:converted str '1911-11-13T04' to datetime
uxflint.py:l58.uxf:26:#485:converted str '1913-12-01T05:19' to datetime
uxflint.py:l58.uxf:29:#488:expected str, got <class 'int'> 3
uxflint.py:l58.uxf:29:#488:expected str, got <class 'int'> 4
uxflint.py:l58.uxf:29:#488:expected str, got <class 'float'> 5.6
uxflint.py:l58.uxf:29:#488:expected str, got <class 'float'> -7.9
uxflint.py:l58.uxf:29:#488:expected str, got <class 'int'> -8
uxflint.py:l58.uxf:29:#488:expected str, got <class 'datetime.date'> \
1990-01-11
uxflint.py:l58.uxf:29:#488:expected str, got <class 'datetime.datetime'> \
1995-03-15 22:30:00
uxflint.py:l58.uxf:30:#488:expected str, got <class 'datetime.datetime'> \
1998-10-17 20:18:45
uxflint.py:l58.uxf:31:#488:expected str, got <class 'bytes'> b'UXF 1.0'
uxflint.py:l58.uxf:32:#484:expected int, got <class 'str'> one
uxflint.py:l58.uxf:32:#484:expected int, got <class 'str'> two
uxflint.py:l58.uxf:34:#489:converted real to int
uxflint.py:l58.uxf:34:#489:converted real to int
uxflint.py:l58.uxf:34:#488:expected int, got <class 'datetime.date'> \
1990-01-11
uxflint.py:l58.uxf:35:#488:expected int, got <class 'datetime.datetime'> \
1995-03-15 22:30:00
uxflint.py:l58.uxf:35:#488:expected int, got <class 'datetime.datetime'> \
1998-10-17 20:18:45
uxflint.py:l58.uxf:36:#488:expected int, got <class 'bytes'> b'UXF 1.0'
uxflint.py:l58.uxf:36:#492:expected int, got <class 'uxf.Table'> Table \
None [] with 0 records #None
uxflint.py:l58.uxf:36:#484:expected int, got <class 'str'> a
uxflint.py:l58.uxf:36:#484:expected int, got <class 'str'> b
uxflint.py:l58.uxf:38:#520:unused type: 'by'
could have found 66 errors and fixed 40 of them''',
    'l59.uxf': '''
uxflint.py:l59.uxf:20:#530:unused types: 'one', 'three', 'two'
could have found one error but could not fix it''',
    }


if __name__ == '__main__':
    main()
