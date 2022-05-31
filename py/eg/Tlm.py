#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
An example of using UXF as both a "native" file formand and as an exchange
format for importing and exporting. The main class, Tlm holds a track list
and a list of history strings. The Tlm can load and save in its own .tlm
format, and also seamlessly, UXF format.
'''

import collections
import contextlib
import enum
import gzip
import os
import pathlib
import sys

try:
    import mutagen
except ImportError:
    mutagen = None

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
    model = Model(infilename) # this will load from infilename
    model.save(outfilename) # this will save to outfilename

# TODO Update class Model to seamlessly load/save UXF as well as TLM

#class Tlm:
#
#    def __init__(self, filename=None):
#        self.clear()
#        if filename is not None:
#            self.load(filename)
#
#
#    def clear(self):
#        self.tracklist = TrackList()
#        self.history = [] # list of str
#        self.dirty = False
#
#
#    def load(self, filename=None):
#        if filename is not None:
#            self.filename = filename
#        if not self.filename:
#            raise Error('no filename to load')
#        try:
#            try:
#                with gzip.open(filename, 'rt', encoding='utf-8') as file:
#                    data = file.read()
#            except gzip.BadGzipFile:
#                with open(filename, 'rt', encoding='utf-8') as file:
#                    data = file.read()
#        except OSError as err:
#            raise Error(f'failed to read {filename}: {err}')
#        self.clear()
#        if data.startswith('uxf 1.0'):
#            return self._read_uxf(data)
#        else:
#            return self._read_tlm(data)
#
#
#    def _read_tlm(self, data):
#        # TODO read TLM data directly to populate self.tracklist
#        # Copy & adapt convert_to_uxf_old() from below
#        self.dirty = False
#        return True
#
#
#    def _read_uxf(self, data):
#        uxo = uxf.loads(data)
#        # TODO read uxo.data to populate self.tracklist and self.history
#        self.dirty = False
#        return True
#
#
#    def save(self, filename=None):
#        if filename is not None:
#            self.filename = filename
#        if not self.filename:
#            raise Error('no filename to save to')
#        if self.filename.upper().endswith('.TLM'):
#            return self._save_tlm()
#        else:
#            return self._save_uxf()
#
#
#    def _save_tlm(self):
#        with gzip.open(self.filename, 'wt', encoding='utf-8') as file:
#            pass
#            # TODO save the tracklist and history in TLM format (gzipped
#            # since by default .tlm files are gzipped)
#        self.dirty = False
#        return True
#
#
#    def _save_uxf(self):
#        uxo = uxf.Uxf({}, custom='TLM 1.1')
#        # TODO copy the tracklist and history into the uxo
#        uxo.dump(self.filename)
#        self.dirty = False
#        return True


class Error(Exception):
    pass


class Model:

    def __init__(self, filename=None):
        self.clear()
        self._filename = filename
        if self._filename is not None and os.path.exists(self._filename):
            self.load()


    @property
    def filename(self):
        return self._filename


    @filename.setter
    def filename(self, filename):
        self._filename = filename
        if os.path.exists(filename):
            self.load()


    def clear(self):
        self.tree = Group('')
        self.history = collections.deque()


    def load(self, filename=None):
        if filename is not None:
            self._filename = filename
        magics = {TLM_MAGIC.encode('ascii'), UXF_MAGIC.encode('ascii')}
        with open(self._filename, 'rb') as file:
            opener = open if file.read(4) in magics else gzip.open
        self.clear()
        stack = [self.tree]
        prev_indent = 0
        state = _State.WANT_MAGIC
        with opener(self._filename, 'rt', encoding='utf-8') as file:
            for lino, line in enumerate(file, 1):
                line = line.rstrip()
                if not line:
                    continue # ignore blank lines
                if state is _State.IN_TRACKS and line == '\fHISTORY':
                    state = _State.IN_HISTORY
                elif state is _State.WANT_MAGIC:
                    if not line.startswith(TLM_MAGIC):
                        raise Error(f'error:{lino}: not a .tlm file')
                    # NOTE We ignore the version for now
                    state = _State.WANT_TRACK_HEADER
                elif state is _State.WANT_TRACK_HEADER:
                    if line != '\fTRACKS':
                        raise Error(f'error:{lino}: missing TRACKS')
                    state = _State.IN_TRACKS
                elif state is _State.IN_TRACKS:
                    if line.startswith(INDENT):
                        prev_indent = self._read_group(stack, prev_indent,
                                                       lino, line)
                    elif not line.startswith('\f'):
                        self._read_track(stack[-1], lino, line)
                elif state is _State.IN_HISTORY:
                    self.history.append(line)
                else:
                    raise Error(f'error:{lino}: invalid .tlm file')


    def _read_group(self, stack, prev_indent, lino, line):
        name = line.lstrip(INDENT)
        indent = len(line) - len(name)
        group = Group(name)
        if indent == 1:
            self.tree.append(group)
            stack[:] = [self.tree, group]
        elif indent > prev_indent: # child
            stack[-1].append(group)
            stack.append(group)
        elif indent <= prev_indent: # same level or higher
            for _ in range(prev_indent - indent + 1):
                stack.pop() # move back up to same or higher parent
            stack[-1].append(group)
            stack.append(group)
        return indent


    def _read_track(self, group, lino, line):
        try:
            filename, secs = line.split('\t', maxsplit=1)
            group.append(Track(filename, float(secs)))
        except ValueError as err:
            raise Error(f'error:{lino}: failed to read track: {err}')


    def save(self, *, filename=None, compress=True):
        if filename is not None:
            self._filename = filename
        opener = gzip.open if compress else open
        with opener(self._filename, 'wt', encoding='utf-8') as file:
            file.write('\fTLM\t100\n\fTRACKS\n')
            self._write_tree(file, self.tree)
            file.write('\fHISTORY\n')


    def _write_tree(self, file, tree, depth=1):
        pad = depth * INDENT
        for kid in tree.kids:
            if isinstance(kid, Group):
                file.write(f'{pad}{kid.name}\n')
                self._write_tree(file, kid, depth + 1)
            else:
                file.write(f'{kid.filename}\t{kid.secs:.03f}\n')


    def paths(self):
        for path in self._paths(self.tree, ''):
            yield path


    def _paths(self, tree, prefix):
        prefix = f'{prefix}/{tree.name}' if prefix else tree.name
        if prefix:
            yield prefix
        for kid in tree.kids:
            if isinstance(kid, Group):
                for path in self._paths(kid, prefix):
                    yield path
            elif kid.treename:
                yield f'{prefix}/{kid.treename}'


    def secs_for(self, tree=None):
        if tree is None:
            tree = self.tree
        return self._secs_for(tree)


    def _secs_for(self, tree):
        secs = 0.0
        for kid in tree.kids:
            if isinstance(kid, Group):
                secs += self._secs_for(kid)
            else:
                secs += kid.secs
        return secs


@enum.unique
class _State(enum.Enum):
    WANT_MAGIC = enum.auto()
    WANT_TRACK_HEADER = enum.auto()
    IN_TRACKS = enum.auto()
    IN_HISTORY = enum.auto()


class Group:

    def __init__(self, name):
        self.name = name
        self.kids = []


    def __repr__(self):
        return f'Group({self.name!r})'


    def subgroup(self, group_name):
        for kid in self.kids:
            if kid.name == group_name:
                return kid


    def append(self, group_or_track):
        self.kids.append(group_or_track)


class Track:

    def __init__(self, filename, secs):
        self._filename = filename
        self._title = None
        self._secs = secs
        self._album = None
        self._artist = None
        self._number = 0


    def __repr__(self):
        return f'Track({self.filename!r}, {self.secs:0.3f})'


    def _populate_metadata(self):
        if mutagen is None:
            return

        def get_meta_item(meta, name):
            try:
                return meta[name][0]
            except (KeyError, IndexError):
                pass

        try:
            meta = mutagen.File(self._filename)
            if meta is not None:
                self._title = get_meta_item(meta, 'title')
                self._secs = meta.info.length
                self._album = get_meta_item(meta, 'album')
                self._artist = get_meta_item(meta, 'artist')
                try:
                    self._number = int(meta['tracknumber'][0])
                except (IndexError, ValueError):
                    self._number = 0
                return
        except (mutagen.MutagenError, FileNotFoundError):
            pass
        if self._title is None:
            self._title = (
                os.path.splitext(os.path.basename(self._filename))[0]
                .replace('-', ' ').replace('_', ' '))


    @property
    def filename(self):
        return self._filename


    @property
    def treename(self):
        return (pathlib.Path(self.filename).stem.replace('-', ' ')
                .replace('_', ' ').lstrip('0123456789 '))


    @property
    def title(self):
        if self._title is None:
            self._populate_metadata()
        return self._title


    @property
    def secs(self):
        if self._secs <= 0:
            self._populate_metadata()
        return self._secs


    @property
    def album(self):
        if self._album is None:
            self._populate_metadata()
        return self._album


    @property
    def artist(self):
        if self._artist is None:
            self._populate_metadata()
        return self._artist


    @property
    def number(self):
        if self._number == 0:
            self._populate_metadata()
        return self._number


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


TLM_MAGIC = '\fTLM\t'
INDENT = '\v'
UXF_MAGIC = 'uxf 1.0'
UXF_ROOT = '__ROOT__'
UXF_HISTORY = '__HISTORY__'


if __name__ == '__main__':
    main()
