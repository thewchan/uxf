#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
For another example of this file's merge() function see include.py.
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
        raise SystemExit('''usage: merge.py [-o|--outfile <outfile.uxf> \
<infile1.uxf> <infile2.uxf> [... <infileN.uxf>]''')
    # uxo = merge(...)
    # if outfile and outfile != '-':
    #     uxo.dump(outfile)
    #     print(f'saved {outfile}')
    # else:
    #     print(uxo.dumps())



def merge(file1, file2, *files, aslist=False):
    uxo = uxf.Uxf([] if aslist else {})
    for filename in (file1, file2) + files:
        new_uxo = uxf.load(filename)
        if new_uxo.comment:
            if not uxo.comment:
                uxo.comment = new_uxo.comment
            else:
                uxo.comment += '\n' + new_uxo.comment
        merge_imports(uxo, new_uxo)
        merge_tclasses(uxo, new_uxo, filename)
        if not aslist:
            uxo.append(filename) # key
        uxo.append(new_uxo.data) # value for map or list
    return uxo


def merge_imports(uxo1, uxo2):
    print('merge_imports') # TODO see ../uxfconvert.py _get_imports()


def merge_tclasses(uxo1, uxo2, filename):
    # TODO this accounts for imports if merge_imports() is called first
    for ttype, tclass in uxo2.tclasses.items():
        if ttype not in uxo1.tclasses:
            uxo1.tclasses[ttype] = tclass
        elif uxo1.tclasses[ttype] == tclass:
            pass # same so safe to ignore
        else:
            raise uxf.Error(f'cannot merge {filename} due to conflicting '
                            f'ttype {ttype}')


if __name__ == '__main__':
    main()
