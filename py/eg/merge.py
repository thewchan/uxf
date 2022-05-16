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
    import eq
except ImportError: # needed for development
    PATH = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(PATH + '/..')
    import uxf
    sys.path.append(PATH + '/../t')
    import eq


def main():
    if len(sys.argv) < 2 or sys.argv[1] in {'-h', '--help'}:
        raise SystemExit('''usage: merge.py \
[-l|--list] [-|[-o|--outfile] <outfile>] \
<infile1> <infile2> [... <infileN>]
If -l or --list is specified, the outfile will contain a list where each
value is the contents of an infile. The default is for the outfile to
contain a map where each key is the name of an infile and each value the
contents of the corresponding infile.
The outfile will be in UXF format. If none is specified will output to \
stdout.
Regardless of suffix, all infiles are assumed to be UXF format.''')
    asmap, outfile, infiles = get_config()
    try:
        uxo = merge(*infiles, asmap=asmap)
        if outfile != '-':
            uxo.dump(outfile)
            print(f'saved {outfile}')
        else:
            print(uxo.dumps())
    except uxf.Error as err:
        print(f'failed to merge: {err}')


def get_config():
    outfile = '-'
    infiles = []
    want_outfile = False
    asmap = True
    for arg in sys.argv[1:]:
        if want_outfile:
            outfile = arg
            want_outfile = False
        elif arg in {'-l', '--list'}:
            asmap = False
        elif arg == '-':
            pass # this is the default
        elif arg in {'-o', '--outfile'}:
            want_outfile = True
        elif arg.startswith('-o'):
            outfile = arg[2:]
            if outfile.startswith('='):
                outfile = outfile[1:]
        elif arg.startswith('--outfile'):
            outfile = arg[9:]
            if outfile.startswith('='):
                outfile = outfile[1:]
        else:
            infiles.append(arg)
    return asmap, outfile, infiles


def merge(file1, file2, *files, asmap):
    uxo = uxf.Uxf({} if asmap else [])
    for filename in (file1, file2) + files:
        new_uxo = uxf.load(filename)
        if new_uxo.comment:
            if not uxo.comment:
                uxo.comment = new_uxo.comment
            else:
                uxo.comment += '\n' + new_uxo.comment
        merge_ttypes(uxo, new_uxo, filename)
        if asmap:
            uxo.append(filename) # key
        uxo.append(new_uxo.data) # value for map or list
    return uxo


def merge_ttypes(uxo1, uxo2, filename):
    _merge_imports(uxo1, uxo2)
    _merge_tclasses(uxo1, uxo2, filename)


def _merge_imports(uxo1, uxo2):
    print('merge_imports') # TODO see ../uxfconvert.py _get_imports()


def _merge_tclasses(uxo1, uxo2, filename):
    # *must* be called *after* merge_imports()
    for ttype, tclass in uxo2.tclasses.items():
        if ttype not in uxo1.tclasses:
            uxo1.tclasses[ttype] = tclass
        elif eq.eq(uxo1.tclasses[ttype], tclass, ignore_comments=True):
            pass # same so safe to ignore
        else:
            raise uxf.Error(f'cannot merge {filename} due to conflicting '
                            f'ttype {ttype}')


if __name__ == '__main__':
    main()
