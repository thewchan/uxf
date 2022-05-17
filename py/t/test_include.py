#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import os
import sys

try:
    PATH = os.path.abspath(os.path.dirname(__file__))
    INCLUDE_EXE = os.path.abspath(os.path.join(PATH, '../eg/include.py'))
    os.chdir(os.path.join(PATH, '../../testdata')) # move to test data
finally:
    pass


def main():
    regression = False
    if len(sys.argv) > 1 and sys.argv[1] in {'-r', '--regression'}:
        regression = True
    total = ok = 0

    if not regression: print(INCLUDE_EXE) # TODO delete
    # NOTE See testdata/i68.uxi

    if regression:
        print(f'total={total} ok={ok}')



if __name__ == '__main__':
    main()
