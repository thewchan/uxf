#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
Tests and shows how to convert to/from SQLite.

Such conversions are normally *lossy* in terms of datatypes and structure,
but _not_ in terms of data values of course.

In practice you'd always create your own custom database-specific code and
use the uxf module directly.
'''

import contextlib
import os
import sys
import tempfile


try:
    os.chdir(os.path.dirname(__file__)) # move to this file's dir
    sys.path.append('..')
    import uxf
    import uxfconvert
    import eq
    UXF_EXE = os.path.abspath('../uxf.py')
    UXFCONVERT_EXE = os.path.abspath('../uxfconvert.py')
    os.chdir('../../testdata') # move to test data
finally:
    pass


SUITABLE = ('t15.uxf', 't19.uxf', 't35.uxf', 't36.uxf', 't37.uxf', 't5.uxf')


def main():
    verbose = True
    if len(sys.argv) > 1 and sys.argv[1] in {'-q', '--quiet'}:
        verbose = False
    for name in SUITABLE:
        check(name, verbose)


def check(name, verbose):
    uxo1 = uxf.load(name)
    filename = os.path.join(tempfile.gettempdir(), name.replace('.uxf',
                                                                '.sqlite'))
    with contextlib.suppress(FileNotFoundError):
        os.remove(filename)
    if isinstance(uxo1.data, uxf.Table):
        uxo1.data = [uxo1.data]
    uxfconvert._inner_uxf_to_sqlite(filename, uxo1.data)
    uxo2 = uxfconvert._inner_sqlite_to_uxf(filename)
    if not eq.eq(uxo1, uxo2, ignore_custom=True, ignore_comments=True,
                 ignore_types=True):
        if verbose:
            print(f'test_sqlite • {name} FAIL')
        sys.exit(1)
    if verbose:
        print(f'test_sqlite • {name} OK')
    with contextlib.suppress(FileNotFoundError):
        os.remove(filename)


if __name__ == '__main__':
    main()
