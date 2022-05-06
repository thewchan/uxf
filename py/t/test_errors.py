#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import collections
import sys


try:
    import os
    os.chdir(os.path.dirname(__file__)) # move to this file's dir
    sys.path.append('..')
    import uxf
    UXF_EXE = os.path.abspath('../uxf.py')
    os.chdir('../../testdata') # move to test data
finally:
    pass


def main():
    verbose = True
    if len(sys.argv) > 1 and sys.argv[1] in {'-q', '--quiet'}:
        verbose = False

    try:
        e = 100
        uxf.Uxf(collections.deque((1, 2, 3)))
        fail(f'test_errors • #{e} FAIL', verbose)
    except uxf.Error as err:
        on_error(e, err, verbose)

    table = uxf.Table(name='Pair', fields=('first', 'second'))

    uxo = uxf.Uxf({})
    uxo.data.append('key')
    uxo.data.append('value')
    try:
        e = 120
        uxo.data.append(table)
        fail(f'test_errors • #{e} FAIL', verbose)
    except uxf.Error as err:
        on_error(e, err, verbose)
    try:
        e = 130
        uxo.data.append(3.8)
        fail(f'test_errors • #{e} FAIL', verbose)
    except uxf.Error as err:
        on_error(e, err, verbose)

    try:
        e = 150
        _ = uxf.Field('1st')
        fail(f'test_errors • #{e} FAIL', verbose)
    except uxf.Error as err:
        on_error(e, err, verbose)
    try:
        e = 160
        _ = uxf.Field('$1st')
        fail(f'test_errors • #{e} FAIL', verbose)
    except uxf.Error as err:
        on_error(e, err, verbose)

    try:
        e = 180
        _ = uxf.Table(records=(1, 2))
        fail(f'test_errors • #{e} FAIL', verbose)
    except uxf.Error as err:
        on_error(e, err, verbose)

    try:
        e = 190
        _ = uxf.Table(name='test', records=(1, 2))
        fail(f'test_errors • #{e} FAIL', verbose)
    except uxf.Error as err:
        on_error(e, err, verbose)

    # TODO 219 ...


def on_error(code, err, verbose):
    if not str(err).startswith(f'#{code}'):
        fail(f'test_errors • expected #{code} got, {err} FAIL', verbose)


def fail(message, verbose):
    if verbose:
        print(message)
    sys.exit(1)


if __name__ == '__main__':
    main()
