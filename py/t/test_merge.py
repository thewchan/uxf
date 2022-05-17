#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3


import contextlib
import functools
import os
import sys
import tempfile

try:
    PATH = os.path.abspath(os.path.dirname(__file__))
    MERGE_EXE = os.path.abspath(os.path.join(PATH, '../eg/merge.py'))
    os.chdir(os.path.join(PATH, '../../testdata')) # move to test data
finally:
    pass


def main():
    regression = False
    if len(sys.argv) > 1 and sys.argv[1] in {'-r', '--regression'}:
        regression = True
    total = ok = 0

    if not regression: print(MERGE_EXE) # TODO delete

    if regression:
        print(f'total={total} ok={ok}')



if __name__ == '__main__':
    main()
