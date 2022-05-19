#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import gzip
import os
import sys

try:
    import uxf
except ImportError: # needed for development
    sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../py'))
    import uxf


def main():
    if len(sys.argv) == 1 or sys.argv[1] in {'-h', '--help'}:
        raise SystemExit('usage: tlm2uxf.py <filename.tlm>')
    infilename = sys.argv[1]
    outfilename = infilename.replace('.tlm', '.uxf.gz')
    infile = None
    try:
        infile = open_file(infilename, 'rt')
        trackclass = uxf.TClass('Track', (uxf.Field('filename', 'str'),
                                          uxf.Field('seconds', 'real')))
        uxo = uxf.Uxf({}, custom='TLM 1.1')
        intracks = True
        stack = [ROOT]
        prevlistname = None
        for line in infile:
            if line.startswith(('\fTLM', '\fTRACKS')):
                pass
            elif line.startswith('\fHISTORY'):
                intracks = False
            elif line.startswith('\v'):
                depth = line.count('\v')
                listname = '_' + line.lstrip('\v').rstrip()
                if depth > len(stack):
                    stack.append(prevlistname)
                else:
                    while depth < len(stack):
                        stack.pop()
                prevlistname = listname
                parent = find_parent(uxo, stack)
                parent[listname] = uxf.Map()
            elif intracks:
                filename, seconds = line.rstrip().split('\t')
                if listname not in parent:
                    parent[listname] = uxf.Table(ttype=trackclass)
                parent[listname].append(filename)
                parent[listname].append(float(seconds))
            else: # history
                if HISTORY not in uxo.data:
                    uxo.data[HISTORY] = uxf.List()
                uxo.data[HISTORY].append(line.strip())
        uxo.dump(outfilename)
        print('wrote', outfilename)
    finally:
        if infile is not None:
            infile.close()


def find_parent(uxo, stack):
    for name in stack:
        parent = uxo.data if name == ROOT else parent[name]
    return parent


def open_file(filename, mode):
    try:
        return gzip.open(filename, mode, encoding='utf-8')
    except gzip.BadGzipFile:
        return open(filename, mode, encoding='utf-8')


ROOT = '__ROOT__'
HISTORY = '__HISTORY__'

if __name__ == '__main__':
    main()
