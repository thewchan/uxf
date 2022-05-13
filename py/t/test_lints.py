#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import os
import re
import subprocess
import sys


PATH = os.path.abspath(os.path.dirname(__file__))
UXF_EXE = os.path.join(PATH, '../uxf.py')
os.chdir(os.path.join(PATH, '../../testdata')) # move to test data


ERROR_FILES = {'t13.uxf', 't14.uxf', 't28.uxf', 't33.uxf', 't54.uxf',
               't55.uxf', 'l56.uxf', 'l57.uxf', 'l58.uxf', 'l59.uxf',
               'l60.uxf'}


def main():
    regression = False
    if len(sys.argv) > 1 and sys.argv[1] in {'-r', '--regression'}:
        regression = True
    total = ok = 0

    good_files = {name for name in os.listdir('.')
                  if os.path.isfile(name) and name.endswith(('.uxf',
                                                             '.uxf.gz'))}
    bad_files = ERROR_FILES
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
    cmd = [UXF_EXE, name, '--lint']
    reply = subprocess.run(cmd, capture_output=True, text=True)
    cmd = ' '.join(cmd)
    if reply.returncode != 0 or reply.stderr:
        if not regression:
            text = reply.stderr.strip()
            print(f'{cmd} • (good) FAIL got: {text[:80]!r}…')
        return 0
    return 1


def check_bad(name, regression):
    cmd = [UXF_EXE, name, '--lint']
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
    expected = None
    if name in ERROR_FILES:
        match = re.fullmatch(r'\D+(?P<n>\d+)\.uxf', name)
        if match:
            with open(f'expected/e{match.group("n")}.txt', 'rt',
                      encoding='utf-8') as file:
                expected = file.read().strip()
        else:
            print('test_lints.py internal error')
    if expected is None:
        if actual == 'no errors found':
            return 1
        if not regression:
            print(f'{cmd} • (bad) FAIL expected nothing, '
                  f'got: {actual[:60]!r}…')
        return 0
    if expected != actual:
        if not regression:
            print(f'{cmd} • (bad) FAIL\nEXPECTED {expected[:60]!r}…,\n'
                  f'ACTUAL   {actual[:60]!r}…')
        return 0
    return 1


def by_number(s):
    match = re.fullmatch(r'\D+(?P<n>\d+)\.uxf', s)
    if match is not None:
        return int(match['n']), s
    return 0, s


if __name__ == '__main__':
    main()
