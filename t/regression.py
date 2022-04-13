#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import filecmp
import os
import re
import subprocess
import sys
import time

os.chdir(os.path.dirname(__file__))


def main():
    uxf, uxfconvert, verbose = get_config()
    cleanup()
    t = time.monotonic()
    uxffiles = sorted((name for name in os.listdir('.')
                       if os.path.isfile(name) and name.endswith('.uxf')),
                      key=by_number)
    total, ok = test_uxf(uxf, uxffiles, verbose=verbose)
    total, ok = test_uxfconvert(uxfconvert, uxffiles, total, ok,
                                verbose=verbose)
    if total == ok:
        t = time.monotonic() - t
        print(f'{ok}/{total} All OK ({t:.3f} sec)')
        cleanup()
    else:
        print(f'{ok}/{total} FAIL')


def get_config():
    uxf = '../py/uxf.py'
    uxfconvert = '../py/uxfconvert.py'
    verbose = False
    for arg in sys.argv[1:]:
        if arg in {'-h', '--help'}:
            raise SystemExit('usage: regression.py [path/to/uxf-exe]')
        elif arg in {'-v', '--verbose', 'verbose'}:
            verbose = True
        else:
            uxf = arg
            uxfconvert = os.path.join(os.path.dirname(uxf, 'uxfconvert.py'))
    return uxf, uxfconvert, verbose


def test_uxf(uxf, uxffiles, *, verbose):
    total = ok = 0
    for name in uxffiles:
        total += 1
        actual = f'actual/{name}'
        expected = f'expected/{name}'
        cmd = [uxf, name, actual]
        reply = subprocess.call(cmd)
        cmd = ' '.join(cmd)
        if reply != 0:
            print(f'{cmd} • FAIL (execute)')
        else:
            ok += compare(cmd, name, actual, expected, verbose=verbose)
    return total, ok


def test_uxfconvert(uxfconvert, uxffiles, total, ok, *, verbose):
    files = [(name, name.replace('.uxf', '.json')) for name in uxffiles]
    files += [('t1.uxf', 't1.csv'), ('t2.uxf', 't2.csv'),
              ('0.csv', '0.uxf'), ('1.csv', '1.uxf'), ('2.csv', '2.uxf')]
    # TODO add tests for ini, sqlite, and xml
    for infile, outfile in files:
        total += 1
        actual = f'actual/{outfile}'
        cmd = ([uxfconvert, '-f', infile, actual] if infile == '1.csv' else
               [uxfconvert, infile, actual])
        reply = subprocess.call(cmd)
        cmd = ' '.join(cmd)
        if reply != 0:
            print(f'{cmd} • FAIL (execute)')
        else:
            expected = f'expected/{outfile}'
            ok += compare(cmd, infile, actual, expected, verbose=verbose)
    total += 1
    actual = 'actual/1-2-csv.uxf'
    infile = '1.csv 2.csv'
    cmd = [uxfconvert, '-f', '1.csv', '2.csv', actual]
    reply = subprocess.call(cmd)
    cmd = ' '.join(cmd)
    if reply != 0:
        print(f'{cmd} • FAIL (execute)')
    else:
        expected = 'expected/1-2-csv.uxf'
        ok += compare(cmd, infile, actual, expected, verbose=verbose)
    return total, ok


def compare(cmd, infile, actual, expected, *, verbose):
    try:
        if filecmp.cmp(actual, expected, False):
            if verbose:
                print(f'{cmd} • {infile} → {actual} OK')
            return 1
        else:
            print(f'{cmd} • FAIL (compare)')
    except FileNotFoundError:
        print(f'{cmd} • FAIL (missing {expected!r})')
    return 0


def cleanup():
    if os.path.exists('actual'):
        for name in os.listdir('actual'):
            name = f'actual/{name}'
            if os.path.isfile(name):
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