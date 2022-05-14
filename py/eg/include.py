#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
uxf 1.0 UXF Include
#<e.g., include.uxf>
=include filename:str
(include
  <file1.uxf>
  <file2.uxf>
  <file3.uxf>
)
'''

import os
import sys

try:
    import uxf
except ImportError: # needed for development
    sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
    import uxf


def main():
    if len(sys.argv) < 2 or sys.argv[1] in {'-h', '--help'}:
        raise SystemExit('usage: include.py <include.uxf> [<outfile.uxf>]')
    tclasses = {}
    data = uxf.List()
    uxo = uxf.load(sys.argv[1])
    for record in uxo.data:
        temp_uxo = uxf.load(record.filename)
        data.append(temp_uxo.data)
        # TODO see merge.py for merge_imports() & merge_tclasses()
    uxo.tclasses = tclasses
    uxo.data = data
    if len(sys.argv) > 2:
        uxo.dump(sys.argv[2])
    else:
        print(uxo.dumps())


if __name__ == '__main__':
    main()
