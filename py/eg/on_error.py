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
    # TODO read .uxf files (or use loads()) which generate errors but using
    # on_error=on_error
    show_errors() # if a fatal error occurs before this, show_errors() will
                  # be called anyway


def on_error(...):
    text = f'...'
    on_error.errors.append(text)
    if fail:
        show_errors(1)
on_error.errors = [] # noqa: E305


def show_errors(exit=0):
    if on_error.errors:
        uxo = uxf.Uxf(on_error.errors) # list of str
        print(uxo.dumps())
    sys.exit(exit)


if __name__ == '__main__':
    main()
