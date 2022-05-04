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
    os.chdir(os.path.dirname(__file__)) # MUST come before import uxf
    import uxf
    import uxfconvert
    import eq
    os.chdir('../t')
except ImportError:
    pass # shouldn't happen


SUITABLE = ('t15.uxf', 't19.uxf', 't35.uxf', 't36.uxf', 't37.uxf', 't5.uxf')


def main():
    verbose = True
    if len(sys.argv) > 1 and sys.argv[1] in {'-q', '--quiet'}:
        verbose = False
    for name in SUITABLE[:1]:
        check(name, verbose)


def check(name, verbose):
    uxd1 = uxf.load(name)
    filename = os.path.join(tempfile.gettempdir(), name.replace('.uxf',
                                                                '.sqlite'))
    with contextlib.suppress(FileNotFoundError):
        os.remove(filename)
    uxfconvert._uxf_to_sqlite(filename, uxd1.data)
    uxd2 = uxfconvert._sqlite_to_uxf(filename)
    if not eq.eq(uxd1, uxd2, ignore_custom=True, ignore_comments=True):
        uxd1.dump('/tmp/1')#TODO
        uxd2.dump('/tmp/2')#TODO
        if verbose:
            print(f'test_sqlite • {name} FAIL')
        sys.exit(1)
    if verbose:
        print(f'test_sqlite • {name} OK')
    with contextlib.suppress(FileNotFoundError):
        os.remove(filename)


if __name__ == '__main__':
    main()
