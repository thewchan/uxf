#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
An example of using UXF as an exchange format for importing and exporting.
'''

# TODO
# - implement class Tracks (holds the root TrackList and a list of history strs)
# - implement class TrackList (holds a sequence of Tracks and nested TrackLists)
# - implement class Track (holds one track)
# - implement Tracks.load(tlmfilename) to
#   - delete the root and history
#   - read all the tracks from a .tlm to populate the root and history
# - implement Tracks.save(tlmfilename) to
#   - write all the tracks and history to a .tlm
# - implement Tracks.export_uxf(uxffilename) to
#   - create and populate a Uxf with all the data and dump the Uxf as a .uxf.gz
# - implement Tracks.import_uxf(uxffilename) to
#   - delete the root and history
#   - read all the tracks from a .uxf{.gz} into a Tracks to populate the
#     root and history
# - implement convert_to_uxf(tlmfilename, uxffilename):
#   tracks = Tracks(tlmfilename) # if tlmfilename is not None calls .load()
#   tracks.export_uxf(uxffilename)
# - implement convert_to_tlm(uxffilename, tlmfilename)
#   tracks = Tracks() # empty
#   tracks.import_uxf(uxffilename)
#   tracks.save(tlmfilename)

import contextlib
import gzip
import os
import sys

try:
    import uxf
except ImportError: # needed for development
    sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
    import uxf


def main():
    if len(sys.argv) != 3 or sys.argv[1] in {'-h', '--help'}:
        raise SystemExit('''
usage: tlm_uxf.py <infile.{tlm,uxf,uxf.gz}> <outfile.{tlm,uxf,uxf.gz}>

e.g., tlm_uxf.py tlm-eg.uxf.gz test.tlm''')
    infilename = sys.argv[1]
    outfilename = sys.argv[2]
    with contextlib.suppress(FileNotFoundError):
        if os.path.samefile(infilename, outfilename):
            raise SystemExit('can\'t overwrite infile with outfile')
    if os.path.splitext(infilename)[1] == os.path.splitext(outfilename)[1]:
        raise SystemExit('can only convert to/from UXF from/to TLM')
    elif infilename.endswith('.tlm'):
        convert_to_uxf_old(infilename, outfilename)
    elif infilename.endswith(('.uxf', '.uxf.gz')):
        convert_to_tlm(infilename, outfilename)
    else:
        raise SystemExit('can only convert to/from .uxf{.gz} from/to .tlm')


def convert_to_uxf_old(infilename, outfilename):
    print('convert_to_uxf_old', infilename, outfilename)
    infile = None
    try:
        infile = open_file(infilename, 'rt')
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
                    parent[listname] = uxf.Map()
                parent[listname][filename] = float(seconds)
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
    parent = None
    for name in stack:
        parent = uxo.data if name == ROOT else parent[name]
    return parent


def open_file(filename, mode):
    try:
        return gzip.open(filename, mode, encoding='utf-8')
    except gzip.BadGzipFile:
        return open(filename, mode, encoding='utf-8')


def convert_to_tlm(infilename, outfilename):
    print('convert_to_tlm', infilename, outfilename)


ROOT = '__ROOT__'
HISTORY = '__HISTORY__'


if __name__ == '__main__':
    main()
