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

import os
import sys

try:
    os.chdir(os.path.dirname(__file__)) # MUST come before import uxf
    import uxf
    import uxfconvert
    os.chdir('../t')
except ImportError:
    pass # shouldn't happen


SUITABLE = ('t5.uxf', 't15.uxf', 't19.uxf', 't35.uxf', 't36.uxf', 't37.uxf')


def main():
    verbose = True
    if len(sys.argv) > 1 and sys.argv[1] in {'-q', '--quiet'}:
        verbose = False
    for name in SUITABLE:
        check(name)


def check(name):
    uxd1 = uxf.load(name)
    # 1. use uxfconvert to save as sqlite in temp
    # 2. use uxfconvert to loads from sqlite in temp
    # 3. compare uxt1 vs uxt2

#    if uxt1 != uxt2:
#        fail(f'test_sqlite • {name} FAIL', verbose)
#    if verbose:
#        print(uxt1, end='')
#        print(f'test_sqlite • {name} OK')


if __name__ == '__main__':
    main()
