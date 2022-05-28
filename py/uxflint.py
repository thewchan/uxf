#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import os
import sys

import uxf


def main():
    if len(sys.argv) == 1 or sys.argv[1] in {'-h', '--help'}:
        raise SystemExit('usage: uxflint.py <file1> [file2 [file3 ...]]')
    for filename in sys.argv[1:]:
        if os.path.isfile(filename):
            try:
                uxf.load(filename, on_error=on_error)
            except (uxf.Error, OSError) as err:
                print(f'uxflint.py:{filename}:{err}')


def on_error(lino, code, message, *, filename='-', fail=False,
             verbose=True):
    fail = 'fatal:' if fail else ''
    print(f'uxflint.py:{filename}:{lino}:{fail}#{code}:{message}')


if __name__ == '__main__':
    main()
