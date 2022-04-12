#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import filecmp
import os
import re
import subprocess
import sys

os.chdir(os.path.dirname(__file__))


def main():
    uxf, uxfconvert = get_exes()
    cleanup()
    uxffiles = sorted((name for name in os.listdir('.')
                       if os.path.isfile(name) and name.endswith('.uxf')),
                      key=by_number)
    total, ok = test_uxf(uxf, uxffiles)
    total, ok = test_uxfconvert(uxfconvert, uxffiles, total, ok)
    print(f'{ok}/{total}', 'All OK' if total == ok else 'FAIL')
    if total == ok:
        cleanup()


def get_exes():
    uxf = '../py/uxf.py'
    uxfconvert = '../py/uxfconvert.py'
    if len(sys.argv) > 1:
        if sys.argv[1] in {'-h', '--help'}:
            raise SystemExit('usage: regression.py [path/to/uxf-exe]')
        uxf = sys.argv[1]
        uxfconvert = os.path.join(os.path.dirname(uxf, 'uxfconvert.py'))
    return uxf, uxfconvert


def test_uxf(uxf, uxffiles):
    total = ok = 0
    for name in uxffiles:
        total += 1
        actual = f'actual/{name}'
        expected = f'expected/{name}'
        reply = subprocess.call([uxf, name, actual])
        if reply != 0:
            print(f'uxf: {name} FAIL could not output {actual}')
        else:
            ok += compare('uxf', name, actual, expected)
    return total, ok


def test_uxfconvert(uxfconvert, uxffiles, total, ok):
    files = [(name, name.replace('.uxf', '.json')) for name in uxffiles]
    files += [('test1.uxf', 'test1.csv'), ('test2.uxf', 'test2.csv'),
              ('0.csv', '0.uxf'), ('1.csv', '1.uxf')]
    # TODO add tests for ini, sqlite, and xml
    for infile, outfile in files:
        total += 1
        actual = f'actual/{outfile}'
        args = ([uxfconvert, '-f', infile, actual] if infile == '1.csv' else
                [uxfconvert, infile, actual])
        reply = subprocess.call(args)
        if reply != 0:
            print(f'uxfconvert: {infile} FAIL could not output {actual}')
        else:
            expected = f'expected/{outfile}'
            ok += compare('uxfconvert', infile, actual, expected)
    total += 1
    actual = 'actual/1-2-csv.uxf'
    infile = '1.csv 2.csv'
    reply = subprocess.call([uxfconvert, '-f', '1.csv', '2.csv', actual])
    if reply != 0:
        print(f'uxfconvert: {infile} FAIL could not output {actual}')
    else:
        expected = 'expected/1-2-csv.uxf'
        ok += compare('uxfconvert', infile, actual, expected)
    return total, ok


def compare(cmd, infile, actual, expected):
    try:
        if filecmp.cmp(actual, expected, False):
            print(f'{cmd}: {infile} → {actual} OK')
            return 1
        else:
            print(f'{cmd}: {infile} FAIL {expected} != {actual}')
    except FileNotFoundError:
        print(f'{cmd}: {infile} FAIL missing: {expected}')
    return 0


def cleanup():
    if os.path.exists('actual'):
        for name in os.listdir('actual'):
            name = f'actual/{name}'
            if os.path.isfile(name) and name.endswith('.uxf'):
                os.remove(name)
    else:
        os.mkdir('actual')


def by_number(s):
    match = re.match(r'(?P<name>\D+)(?P<number>\d+)', s)
    if match is not None:
        return match['name'], int(match['number'])
    return s, 0


if __name__ == '__main__':
    main()
