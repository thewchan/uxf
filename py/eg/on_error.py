#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import os
import sys

try:
    import uxf
except ImportError: # needed for development
    sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
    import uxf


def main():
    if len(sys.argv) < 2 or sys.argv[1] in {'-h', '--help'}:
        raise SystemExit('''usage: on_error.py <infile1.uxf> \
[<infile2.uxf> [... <infileN.uxf>]]''')
    # TODO see paper notes


if __name__ == '__main__':
    main()
