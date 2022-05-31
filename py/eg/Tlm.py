#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
An example of using UXF as both a "native" file formand and as an exchange
format for importing and exporting. The main class, Tlm holds a track list
and a list of history strings. The Tlm can load and save in its own .tlm
format, and also seamlessly, UXF format.
'''

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
usage: Tlm.py <infile.{tlm,uxf,uxf.gz}> <outfile.{tlm,uxf,uxf.gz}>

e.g., Tlm.py tlm-eg.uxf.gz test.tlm''')
    infilename = sys.argv[1]
    outfilename = sys.argv[2]
    with contextlib.suppress(FileNotFoundError):
        if os.path.samefile(infilename, outfilename):
            raise SystemExit('can\'t overwrite infile with outfile')
    inext = os.path.splitext(infilename)[1].upper()
    outext = os.path.splitext(outfilename)[1].upper()
    if inext == outext or (inext != '.TLM' and outext != '.TLM'):
        # the extensions must be different from each other and one must be
        # .tlm
        raise SystemExit('can only convert to/from UXF from/to TLM')
    tlm = Tlm(infilename) # this will load from infilename
    tlm.save(outfilename) # this will save to outfilename


class Tlm:

    def __init__(self, filename=None):
        self.clear()
        if filename is not None:
            self.load(filename)


    def clear(self):
        self.tracklist = TrackList()
        self.history = [] # list of str
        self.dirty = False


    def load(self, filename=None):
        if filename is not None:
            self.filename = filename
        if not self.filename:
            raise Error('no filename to load')
        try:
            try:
                with gzip.open(filename, 'rt', encoding='utf-8') as file:
                    data = file.read()
            except gzip.BadGzipFile:
                with open(filename, 'rt', encoding='utf-8') as file:
                    data = file.read()
        except OSError as err:
            raise Error(f'failed to read {filename}: {err}')
        self.clear()
        if data.startswith('uxf 1.0'):
            return self._read_uxf(data)
        else:
            return self._read_tlm(data)


    def _read_tlm(self, data):
        # TODO read TLM data directly to populate self.tracklist
        # Copy & adapt convert_to_uxf_old() from below
        self.dirty = False
        return True


    def _read_uxf(self, data):
        uxo = uxf.loads(data)
        # TODO read uxo.data to populate self.tracklist and self.history
        self.dirty = False
        return True


    def save(self, filename=None):
        if filename is not None:
            self.filename = filename
        if not self.filename:
            raise Error('no filename to save to')
        if self.filename.upper().endswith('.TLM'):
            return self._save_tlm()
        else:
            return self._save_uxf()


    def _save_tlm(self):
        with gzip.open(self.filename, 'wt', encoding='utf-8') as file:
            pass
            # TODO save the tracklist and history in TLM format (gzipped
            # since by default .tlm files are gzipped)
        self.dirty = False
        return True


    def _save_uxf(self):
        uxo = uxf.Uxf({}, custom='TLM 1.1')
        # TODO copy the tracklist and history into the uxo
        uxo.dump(self.filename)
        self.dirty = False
        return True


class TrackList:

    def __init__(self):
        self.kids = [] # each may be a Track or TrackList; so recursive


class Track:

    def __init__(self, filename, seconds: float):
        self.filename = filename
        self.seconds = seconds


class Error(Exception):
    pass


###### TODO delete

def convert_to_uxf_old(infilename, outfilename):
    print('convert_to_uxf_old', infilename, outfilename)
    infile = None
    try:
        infile = open_file(infilename, 'rt')
        uxo = uxf.Uxf({}, custom='TLM 1.1')
        intracks = True
        stack = [UXF_ROOT]
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
                if UXF_HISTORY not in uxo.data:
                    uxo.data[UXF_HISTORY] = uxf.List()
                uxo.data[UXF_HISTORY].append(line.strip())
        uxo.dump(outfilename)
        print('wrote', outfilename)
    finally:
        if infile is not None:
            infile.close()


def find_parent(uxo, stack):
    parent = None
    for name in stack:
        parent = uxo.data if name == UXF_ROOT else parent[name]
    return parent


def open_file(filename, mode):
    try:
        return gzip.open(filename, mode, encoding='utf-8')
    except gzip.BadGzipFile:
        return open(filename, mode, encoding='utf-8')


UXF_ROOT = '__ROOT__'
UXF_HISTORY = '__HISTORY__'


if __name__ == '__main__':
    main()
