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
    't13.uxf': ('uxflint.py:t13.uxf:5,6,7,8,9:#542:ttypes Playlists, '
                'IPv4, RGB, RGBA, IntPair are unused'),
    't14.uxf': ('uxflint.py:t14.uxf:3,4,5,6,7,8:#542:ttypes Categories, '
                'Playlists, IPv4, RGB, RGBA, IntPair are unused'),
    't24.uxf': ("uxflint.py:t24.uxf:4:#492:expected list, got "
                "<class 'uxf.Table'> Table None [] with 0 records "
                "#None\nuxflint.py:t24.uxf:14:#492:expected list, "
                "got <class 'uxf.Table'> Table None [] with 0 records "
                "#None"),
    't28.uxf': ('uxflint.py:t28.uxf:4,5,6,7,8:#542:ttypes Playlists, '
                'IPv4, RGB, RGBA, IntPair are unused'),
    't33.uxf': ("uxflint.py:t33.uxf:10:#492:expected map, got "
                "<class 'uxf.Table'> Table None [] with 0 records #None"),
    't54.uxf': ("uxflint.py:t54.uxf:3:#540:ttype 'Pair' is unused"),
    't55.uxf': ("uxflint.py:t55.uxf:3:#540:ttype 'Pair' is unused"),
    't56.uxf': '''
uxflint.py:t56.uxf:8:#485:converted str '2' to int
uxflint.py:t56.uxf:8:#485:converted str '1983-04-07' to date
uxflint.py:t56.uxf:10:#489:converted real to int
uxflint.py:t56.uxf:14:#484:expected real, got <class 'str'> wrong
uxflint.py:t56.uxf:17:#487:converted int to real
uxflint.py:t56.uxf:19:#485:converted str '6.7' to real
uxflint.py:t56.uxf:20:#485:converted str '9' to real
uxflint.py:t56.uxf:21:#487:converted int to real
uxflint.py:t56.uxf:22:#487:converted int to real
uxflint.py:t56.uxf:23:#487:converted int to real
uxflint.py:t56.uxf:24:#487:converted int to real
uxflint.py:t56.uxf:24:#485:converted str '2008-09-01T23:59:46' to datetime
''',
    }


if __name__ == '__main__':
    main()
