#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
UXF is a plain text human readable optionally typed storage format. UXF may
serve as a convenient alternative to csv, ini, json, sqlite, toml, xml, or
yaml.

The uxf module can be used as an executable. To see the command line help run:

    python3 -m uxf -h

or

    path/to/uxf.py -h

The uxf module distinguishes between a ttype (the name of a user-defined
table) and a TClass (the Python class which represents a user-defined
table). A TClass has a .ttype attribute and a .fields attribute (see below).

The uxf module's public API provides the following free functions and
classes.

    load(filename_or_filelike): -> uxo
    loads(uxt): -> uxo

These functions read UXF data from a file, file-like, or string.
The returned uxo is of type Uxf (see below).
See the function docs for additional options.

In the docs we use uxo to refer to a Uxf object and uxt to refer to a string
containing a UXF file's text.

    dump(filename_or_filelike, data)
    dumps(data) -> uxt

These functions write UXF data to a file, file-like, or string.
The data can be a Uxf object or a single list, List, dict, Map, or Table.
dump() writes the data to the filename_or_filelike; dumps() writes the data
into a string that's then returned. See the function docs for additional
options.

    on_error(...)

This is the default error handler which you can replace by passing a new one
to load(s) and dump(s). For examples of custom on_error functions, see
t/test_errors.py and eg/on_error.py.

    add_converter(obj_type, to_str, from_str)

This function can be used to register custom types and custom converters
to/from strings. (See test_converter.py examples of use.)

    naturalize(s) -> object

This function takes a str and returns a bool or datetime.datetime or
datetime.date or int or float if any of these can be parsed, otherwise
returns the original string s. This is provided as a helper function (e.g.,
it is used by uxfconvert.py).

    canonicalize(name)

Given a name, returns a name that is a valid table or field name.

    is_scalar(x) -> bool

Returns True if x is None or a bool, int, float, datetime.date,
datetime.datetime, str, bytes, or bytearray; otherwise returns False.

    Error

This class is used to propagate errors.

(If this module produces an exception that isn't a uxf.Error or IOError
subclass then it is probably a bug that should be reported.)

    Uxf

This class has a .data attribute which holds a Map, List, or Table, a
.custom str holding a (possibly empty) custom string, and a .tclasses
holding a (possibly empty) dict whose names are TClass table names (ttypes)
and whose values are TClasses. It also has convenience dump(), dumps(),
load() and loads() methods.

    List

This class is used to represent a UXF list. It is a collections.UserList
subclass that also has .comment and .vtype attributes.

    Map

This class is used to represent a UXF map. It is a collections.UserDict
subclass that also has .comment, .ktype, and .vtype attributes. It also has
a special append() method.

    Table

This class is used to store UXF Tables. A Table has a TClass (see below) and
a records list which is a list of lists of scalars with each sublist having
the same number of items as the number of fields. It also has .comment,
.ttype (a convenience for .tclass.ttype), and .tclass attributes, and a
special append() method.

    TClass

This class is used to store a Table's ttype (i.e., its name) and fields (see
below).

    Field

This class is used to store a Table's fields. The .name must start with a
letter and be followed by 0-uxf.MAX_IDENTIFIER_LEN-1 letters, digits, or
underscores. A vtype must be one of these strs: 'bool', 'int', 'real',
'date', 'datetime', 'str', 'bytes', or None (which means accept any valid
type), or a ttype name.

Note that the __version__ is the module version (i.e., the versio of this
implementation), while the VERSION is the maximum UXF version that this
module can read (and the UXF version that it writes).
'''

import collections
import datetime
import enum
import functools
import gzip
import io
import os
import pathlib
import sys
import urllib.error
import urllib.request
from xml.sax.saxutils import escape, unescape

try:
    from dateutil.parser import isoparse
except ImportError:
    isoparse = None


__all__ = ('__version__', 'VERSION', 'load', 'loads', 'dump', 'dumps',
           'naturalize', 'canonicalize', 'is_scalar', 'Uxf', 'List',
           'Map', 'Table', 'TClass', 'Field')
__version__ = '0.29.0' # uxf module version
VERSION = 1.0 # uxf file format version

UTF8 = 'utf-8'
MAX_IDENTIFIER_LEN = 60
MAX_LIST_IN_LINE = 10
MAX_SHORT_LEN = 32
_KEY_TYPES = frozenset({'int', 'date', 'datetime', 'str', 'bytes'})
_VALUE_TYPES = frozenset(_KEY_TYPES | {'bool', 'real'})
_ANY_VALUE_TYPES = frozenset(_VALUE_TYPES | {'list', 'map', 'table'})
_BOOL_FALSE = frozenset({'no', 'false'})
_BOOL_TRUE = frozenset({'yes', 'true'})
_CONSTANTS = frozenset(_BOOL_FALSE | _BOOL_TRUE)
_BAREWORDS = frozenset(_ANY_VALUE_TYPES | _CONSTANTS)
RESERVED_WORDS = frozenset(_ANY_VALUE_TYPES | {'null'} | _CONSTANTS)
_MISSING = object()


def on_error(lino, code, message, *, filename, fail=False, verbose=True):
    text = f'uxf.py:{filename}:{lino}:#{code}:{message}'
    if fail:
        raise Error(text)
    if verbose:
        print(text, file=sys.stderr)


class Uxf:
    '''A Uxf object holds three attributes.

    .data is a List, Map, or Table of data
    .custom is an opional custom string used for customizing the file format
    .tclasses is a dict where each key is a ttype (i.e., the .tclass.ttype
    which is a TClass's name) and each value is a TClass object.
    .comment is an optional file-level comment
    '''

    def __init__(self, data=None, *, custom='', tclasses=None,
                 comment=None):
        '''data may be a list, List, tuple, dict, Map, or Table and will
        default to a List if not specified; if given tclasses must be a dict
        whose values are TClasses and whose corresponding keys are the
        TClasses' ttypes (i.e., their names); if given the comment is a
        file-level comment that follows the uxf header and precedes any
        TClasses and data'''
        self.data = data
        self.custom = custom
        self.comment = comment
        # tclasses key=ttype value=TClass
        self.tclasses = tclasses if tclasses is not None else {}
        self.imports = {} # key=ttype value=import text


    @property
    def import_filenames(self):
        seen = set()
        for filename in self.imports.values(): # don't sort!
            if filename not in seen:
                yield filename
                seen.add(filename)


    @property
    def data(self):
        return self._data


    @data.setter
    def data(self, data):
        if data is None:
            data = List()
        elif isinstance(data, list):
            data = List(data)
        elif isinstance(data, dict):
            data = Map(data)
        elif isinstance(data, (set, frozenset, tuple, collections.deque)):
            data = List()
        if not _is_uxf_collection(data):
            raise Error('#100:Uxf data must be a list, List, dict, Map, or '
                        f'Table, got {data.__class__.__name__}')
        self._data = data


    def dump(self, filename_or_filelike, *, indent=2, use_true_false=False,
             on_error=on_error):
        '''Convenience method that wraps the module-level dump() function'''
        dump(filename_or_filelike, self, indent=indent,
             use_true_false=use_true_false, on_error=on_error)


    def dumps(self, *, indent=2, use_true_false=False, on_error=on_error):
        '''Convenience method that wraps the module-level dumps()
        function'''
        return dumps(self, indent=indent, use_true_false=use_true_false,
                     on_error=on_error)


    def load(self, filename_or_filelike, *, on_error=on_error):
        '''Convenience method that wraps the module-level load()
        function'''
        filename = (filename_or_filelike if isinstance(filename_or_filelike,
                    (str, pathlib.Path)) else '-')
        data, custom, tclasses, imports, comment = _loads(
            _read_text(filename_or_filelike), filename, on_error=on_error)
        self.data = data
        self.custom = custom
        self.tclasses = tclasses
        self.comment = comment


    def loads(self, uxt, filename='-', *, on_error=on_error):
        '''Convenience method that wraps the module-level loads()
        function'''
        data, custom, tclasses, imports, comment = _loads(uxt, filename,
                                                          on_error=on_error)
        self.data = data
        self.custom = custom
        self.tclasses = tclasses
        self.comment = comment


def load(filename_or_filelike, *, on_error=on_error, _imported=None):
    '''
    Returns a Uxf object.

    filename_or_filelike is sys.stdin or a filename or an open readable file
    (text mode UTF-8 encoded, optionally gzipped).
    '''
    filename = (filename_or_filelike if isinstance(filename_or_filelike,
                (str, pathlib.Path)) else '-')
    data, custom, tclasses, imports, comment = _loads(
        _read_text(filename_or_filelike), filename, on_error=on_error,
        _imported=_imported)
    uxo = Uxf(data, custom=custom, tclasses=tclasses, comment=comment)
    uxo.imports = imports
    return uxo


def loads(uxt, filename='-', *, on_error=on_error, _imported=None):
    '''
    Returns a Uxf object.

    uxt must be a string of UXF data.
    '''
    data, custom, tclasses, imports, comment = _loads(
        uxt, filename, on_error=on_error, _imported=_imported)
    uxo = Uxf(data, custom=custom, tclasses=tclasses, comment=comment)
    uxo.imports = imports
    return uxo


def _loads(uxt, filename='-', *, on_error=on_error, _imported=None):
    tokens, custom, text = _tokenize(uxt, filename, on_error=on_error)
    data, comment, tclasses, imports = _parse(
        tokens, filename, on_error=on_error, _imported=_imported)
    return data, custom, tclasses, imports, comment


def _tokenize(uxt, filename='-', *, on_error=on_error):
    lexer = _Lexer(filename, on_error=on_error)
    tokens = lexer.tokenize(uxt)
    return tokens, lexer.custom, uxt


def _read_text(filename_or_filelike):
    if not isinstance(filename_or_filelike, (str, pathlib.Path)):
        return filename_or_filelike.read()
    try:
        with gzip.open(filename_or_filelike, 'rt', encoding=UTF8) as file:
            return file.read()
    except gzip.BadGzipFile:
        with open(filename_or_filelike, 'rt', encoding=UTF8) as file:
            return file.read()


class _Lexer:

    def __init__(self, filename, *, on_error=on_error):
        self.filename = filename
        self.on_error = functools.partial(
            on_error, filename=os.path.basename(filename))
        self.clear()


    def error(self, code, message, *, fail=False):
        self.on_error(self.lino, code, message, fail=fail)


    def clear(self):
        self.pos = 0 # current
        self.lino = 0
        self.custom = None
        self.in_tclass = False
        self.tokens = []


    def tokenize(self, uxt):
        self.text = uxt
        self.scan_header()
        self.maybe_read_comment()
        while not self.at_end():
            self.scan_next()
        self.add_token(_Kind.EOF)
        return self.tokens


    def scan_header(self):
        i = self.text.find('\n')
        if i == -1:
            self.error(110, 'missing UXF file header or empty file',
                       fail=True)
        self.pos = i
        parts = self.text[:i].split(None, 2)
        if len(parts) < 2:
            self.error(120, 'invalid UXF file header', fail=True)
        if parts[0] != 'uxf':
            self.error(130, 'not a UXF file', fail=True)
        try:
            version = float(parts[1])
            if version > VERSION:
                self.error(141,
                           f'version ({version}) > current ({VERSION})')
        except ValueError:
            self.error(151, 'failed to read UXF file version number')
        if len(parts) > 2:
            self.custom = parts[2]


    def maybe_read_comment(self):
        self.skip_ws()
        if not self.at_end() and self.text[self.pos] == '#':
            self.pos += 1 # skip the #
            if self.peek() == '<':
                self.pos += 1 # skip the leading <
                value = self.match_to('>', what='comment string')
                self.add_token(_Kind.COMMENT, unescape(value))
            else:
                self.error(160, 'invalid comment syntax: expected \'<\', '
                           f'got {self.peek()}')


    def at_end(self):
        return self.pos >= len(self.text)


    def scan_next(self):
        c = self.getch()
        if c.isspace(): # ignore insignificant whitespace
            if c == '\n':
                self.lino += 1
        elif c == '(':
            if self.peek() == ':':
                self.pos += 1
                self.read_bytes()
            else:
                self.check_in_tclass()
                self.add_token(_Kind.TABLE_BEGIN)
        elif c == ')':
            self.add_token(_Kind.TABLE_END)
        elif c == '[':
            self.check_in_tclass()
            self.add_token(_Kind.LIST_BEGIN)
        elif c == '=':
            self.add_token(_Kind.TCLASS_BEGIN)
            self.in_tclass = True
        elif c == ']':
            self.add_token(_Kind.LIST_END)
        elif c == '{':
            self.check_in_tclass()
            self.add_token(_Kind.MAP_BEGIN)
        elif c == '}':
            self.in_tclass = False
            self.add_token(_Kind.MAP_END)
        elif c == '?':
            self.add_token(_Kind.NULL)
        elif c == '!':
            self.read_imports()
        elif c == '#':
            self.read_comment()
        elif c == '<':
            self.read_string()
        elif c == ':':
            self.read_field_vtype()
        elif c == '-' and self.peek().isdecimal():
            c = self.getch() # skip the - and get the first digit
            self.read_negative_number(c)
        elif c.isdecimal():
            self.read_positive_number_or_date(c)
        elif c.isalpha():
            self.read_name()
        else:
            self.error(170, f'invalid character encountered: {c!r}')


    def check_in_tclass(self):
        if self.in_tclass:
            self.in_tclass = False
            self.add_token(_Kind.TCLASS_END)


    def read_imports(self):
        this_file = _full_filename(self.filename)
        path = os.path.dirname(this_file)
        while True:
            value = self.match_to('\n', what='import')
            value = value.strip()
            if this_file == _full_filename(value, path):
                self.error(176, 'a UXF file cannot import itself',
                           fail=True)
            else:
                self.add_token(_Kind.IMPORT, value)
            if self.peek() == '!':
                self.getch() # skip !
            else:
                break # imports finished


    def read_comment(self):
        if self.tokens and self.tokens[-1].kind in {
                _Kind.LIST_BEGIN, _Kind.MAP_BEGIN,
                _Kind.TABLE_BEGIN, _Kind.TCLASS_BEGIN}:
            if self.peek() != '<':
                self.error(180, 'a str must follow the # comment '
                           f'introducer, got {self.peek()!r}')
            self.pos += 1 # skip the leading <
            value = self.match_to('>', what='comment string')
            self.add_token(_Kind.COMMENT, unescape(value))
        else:
            self.error(190, 'comments may only occur at the start of '
                       'Lists, Maps, Tables, and TClasses')


    def read_string(self):
        value = self.match_to('>', what='string')
        self.add_token(_Kind.STR, unescape(value))


    def read_bytes(self):
        value = self.match_to(':)', what='bytes')
        try:
            self.add_token(_Kind.BYTES, bytes.fromhex(value))
        except ValueError as err:
            self.error(200, f'expected bytes, got {value!r}: {err}')


    def read_negative_number(self, c):
        is_real = False
        start = self.pos - 1
        while not self.at_end() and (c in '.eE' or c.isdecimal()):
            if c in '.eE':
                is_real = True
            c = self.text[self.pos]
            self.pos += 1
        convert = float if is_real else int
        self.pos -= 1 # wind back to terminating non-numeric char
        text = self.text[start:self.pos]
        try:
            value = convert(text)
            self.add_token(_Kind.REAL if is_real else _Kind.INT,
                           -value)
        except ValueError as err:
            self.error(210, f'invalid number: {text!r}: {err}')


    def read_positive_number_or_date(self, c):
        start = self.pos - 1
        is_real, is_datetime, hyphens = self.read_number_or_date_chars(c)
        text = self.text[start:self.pos]
        convert, token = self.get_converter_and_token(is_real, is_datetime,
                                                      hyphens, text)
        try:
            value = convert(text)
            if token is _Kind.DATE and isoparse is not None:
                value = value.date()
            self.add_token(token, value)
        except ValueError as err:
            if is_datetime and len(text) > 19:
                self.reread_datetime(text, convert)
            else:
                self.error(220,
                           f'invalid number or date/time: {text!r}: {err}')


    def read_number_or_date_chars(self, c):
        is_real = is_datetime = False
        hyphens = 0
        while not self.at_end() and (c in '-+.:eETZ' or c.isdecimal()):
            if c in '.eE':
                is_real = True
            elif c == '-':
                hyphens += 1
            elif c in ':TZ':
                is_datetime = True
            c = self.text[self.pos]
            self.pos += 1
        self.pos -= 1 # wind back to terminating non-numeric non-date char
        return is_real, is_datetime, hyphens


    def get_converter_and_token(self, is_real, is_datetime, hyphens, text):
        if is_datetime:
            return self.read_datetime(text)
        if hyphens == 2:
            convert = (datetime.date.fromisoformat if isoparse is None
                       else isoparse)
            return convert, _Kind.DATE
        if is_real:
            return float, _Kind.REAL
        return int, _Kind.INT


    def read_datetime(self, text):
        if isoparse is None:
            convert = datetime.datetime.fromisoformat
            if text.endswith('Z'):
                text = text[:-1] # Py std lib can't handle UTC 'Z'
        else:
            convert = isoparse
        convert = (datetime.datetime.fromisoformat if isoparse is None
                   else isoparse)
        return convert, _Kind.DATE_TIME


    def reread_datetime(self, text, convert):
        try:
            value = convert(text[:19])
            self.add_token(_Kind.DATE_TIME, value)
            self.error(231, f'skipped timezone data, used {text[:19]!r}, '
                       f'got {text!r}')
        except ValueError as err:
            self.error(240, f'invalid datetime: {text!r}: {err}')


    def read_name(self):
        match = self.match_any_of(_BAREWORDS)
        if match in _BOOL_FALSE:
            self.add_token(_Kind.BOOL, False)
            return
        if match in _BOOL_TRUE:
            self.add_token(_Kind.BOOL, True)
            return
        if match in _ANY_VALUE_TYPES:
            self.add_token(_Kind.TYPE, match)
            return
        start = self.pos - 1
        if self.text[start] == '_' or self.text[start].isalpha():
            identifier = self. match_identifier(start, 'identifier')
            self.add_token(_Kind.IDENTIFIER, identifier)
        else:
            i = self.text.find('\n', self.pos)
            text = self.text[self.pos - 1:i if i > -1 else self.pos + 8]
            self.error(250, f'expected const or identifier, got {text!r}')


    def read_field_vtype(self):
        self.skip_ws()
        identifier = self.match_identifier(self.pos, 'field vtype')
        self.add_token(_Kind.TYPE, identifier)


    def peek(self):
        return '\0' if self.at_end() else self.text[self.pos]


    def skip_ws(self):
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            if self.text[self.pos] == '\n':
                self.lino += 1
            self.pos += 1


    def getch(self): # advance
        c = self.text[self.pos]
        self.pos += 1
        return c


    def match_identifier(self, start, what):
        while self.pos < len(self.text):
            if (not self.text[self.pos].isalnum() and
                    self.text[self.pos] != '_'):
                break
            self.pos += 1
        identifier = self.text[start:self.pos][:MAX_IDENTIFIER_LEN]
        if identifier:
            return identifier
        text = self.text[start:start + 10]
        self.error(260, f'expected {what}, got {text}…')


    def match_to(self, target, *, what):
        if not self.at_end():
            i = self.text.find(target, self.pos)
            if i > -1:
                text = self.text[self.pos:i]
                self.lino += text.count('\n')
                self.pos = i + len(target) # skip past target
                return text
        self.error(270, f'unterminated {what}')


    def match_any_of(self, targets):
        if self.at_end():
            return None
        start = self.pos - 1
        for target in sorted(targets, key=lambda t: (len(t), t),
                             reverse=True):
            if self.text.startswith(target, start):
                self.pos += len(target) - 1 # skip past target
                return target


    def add_token(self, kind, value=None):
        self.tokens.append(_Token(kind, value, lino=self.lino))


class Error(Exception):
    pass


class _Token:

    def __init__(self, kind, value=None, lino=0):
        self.kind = kind
        self.value = value # literal, i.e., correctly typed item
        self.lino = lino


    def __str__(self):
        parts = [self.kind.name]
        if self.value is not None:
            parts.append(f'={self.value!r}')
        return f'{self.lino}:{"".join(parts)}'


    def __repr__(self):
        parts = [f'{self.__class__.__name__}({self.kind.name}']
        if self.value is not None:
            parts.append(f', {self.value!r}')
        parts.append(')')
        return ''.join(parts)


@enum.unique
class _Kind(enum.Enum):
    IMPORT = enum.auto()
    TCLASS_BEGIN = enum.auto()
    TCLASS_END = enum.auto()
    TABLE_BEGIN = enum.auto()
    TABLE_END = enum.auto()
    LIST_BEGIN = enum.auto()
    LIST_END = enum.auto()
    MAP_BEGIN = enum.auto()
    MAP_END = enum.auto()
    COMMENT = enum.auto()
    NULL = enum.auto()
    BOOL = enum.auto()
    INT = enum.auto()
    REAL = enum.auto()
    DATE = enum.auto()
    DATE_TIME = enum.auto()
    STR = enum.auto()
    BYTES = enum.auto()
    TYPE = enum.auto()
    IDENTIFIER = enum.auto()
    EOF = enum.auto()


    @property
    def is_scalar(self):
        return self in {_Kind.NULL, _Kind.BOOL, _Kind.INT, _Kind.REAL,
                        _Kind.DATE, _Kind.DATE_TIME, _Kind.STR, _Kind.BYTES}


class List(collections.UserList):

    def __init__(self, *args, **kwargs):
        '''Takes same arguments as list.
        .data holds the actual list
        .comment holds an optional comment
        .vtype holds a UXF type name ('int', 'real', …)'''
        super().__init__(*args, **kwargs)
        self.comment = None
        self.vtype = None


class Map(collections.UserDict):

    def __init__(self, *args, **kwargs):
        '''Takes same arguments as dict.
        .data holds the actual dict
        .comment holds an optional comment
        .ktype and .vtype hold a UXF type name ('int', 'str', …);
        .ktype may only be int, str, bytes, date, or datetime'''
        super().__init__(*args, **kwargs)
        self.comment = None
        self.ktype = None
        self.vtype = None
        self._pending_key = _MISSING


    def append(self, value):
        '''If there's no pending key, sets the value as the pending key;
        otherwise adds a new item with the pending key and this value and
        clears the pending key.'''
        if self._pending_key is _MISSING:
            if not _is_key_type(value):
                prefix = ('map keys may only be of type int, date, '
                          'datetime, str, or bytes, got ')
                if isinstance(value, Table):
                    raise Error(f'#280:{prefix}a Table ( … ), maybe bytes '
                                '(: … :) was intended?')
                else:
                    raise Error(f'#290:{prefix}{value.__class__.__name__} '
                                f'{value!r}')
            self._pending_key = value
        else:
            self.data[self._pending_key] = value
            self._pending_key = _MISSING


    @property
    def _next_is_key(self):
        return self._pending_key is _MISSING


def _check_name(name):
    if not name:
        raise Error('#298:fields and tables must have nonempty names')
    if name[0].isdigit():
        raise Error('#300:names must start with a letter or '
                    f'underscore, got {name}')
    if name in RESERVED_WORDS:
        raise Error('#304:names cannot be the same as built-in type '
                    'names or constants, got {name}')
    for c in name:
        if not (c == '_' or c.isalnum()):
            raise Error('#310:names may only contain letters, digits, '
                        f'or underscores, got {name}')


class TClass:

    def __init__(self, ttype, fields=None, *, comment=None):
        '''The type of a Table
        .ttype holds the tclass's name (equivalent to a vtype or ktype
        name); it may not be the same as a built-in type name or constant
        .fields holds a list of field names or of fields of type Field
        .comment holds an optional comment'''
        self.ttype = ttype
        self.fields = []
        self.comment = comment
        if fields is not None:
            for field in fields:
                if isinstance(field, str):
                    self.fields.append(Field(field))
                else:
                    self.fields.append(field)


    @property
    def ttype(self):
        return self._ttype


    @ttype.setter
    def ttype(self, ttype):
        if ttype is not None:
            _check_name(ttype)
        self._ttype = ttype


    def append(self, name_or_field, vtype=None):
        if isinstance(name_or_field, Field):
            self.fields.append(name_or_field)
        else:
            self.fields.append(Field(name_or_field, vtype))


    def set_vtype(self, index, vtype):
        self.fields[index].vtype = vtype


    def __bool__(self):
        return bool(self.ttype) and bool(self.fields)


    def __hash__(self):
        return hash(self.ttype)


    def __lt__(self, other): # case-insensitive when possible
        uttype = self.ttype.upper()
        uother = other.ttype.upper()
        if uttype != uother:
            return uttype < uother
        return self.ttype < other.ttype


    def __len__(self):
        return len(self.fields)


    def __repr__(self):
        fields = ', '.join(repr(field) for field in self.fields)
        return (f'{self.__class__.__name__}({self.ttype!r}, {fields}, '
                f'comment={self.comment!r})')


class Field:

    def __init__(self, name, vtype=None):
        '''The type of one field in a Table
        .name holds the field's name (equivalent to a vtype or ktype name);
        may not be the same as a built-in type name or constant
        .vtype holds a UXF type name ('int', 'real', …)'''
        self.name = name
        self.vtype = vtype


    @property
    def name(self):
        return self._name


    @name.setter
    def name(self, name):
        _check_name(name)
        self._name = name


    def __repr__(self):
        return f'{self.__class__.__name__}({self.name!r}, {self.vtype!r})'


class Table:
    '''Used to store a UXF table.

    A Table has a list of fields (name, optional type) and a records list
    which is a list of lists of scalars. with each sublist having the same
    number of items as the number of fields. It also has a .comment
    attribute. (Note that the lists in a Table are plain lists not UXF
    Lists.)

    The only type-safe way to add values to a table is via .append() for
    single values or += for single values or a sequence of values.

    When a Table is iterated each row is returned as a namedtuple.
    '''

    def __init__(self, *, ttype=None, fields=None, records=None,
                 comment=None):
        '''
        A Table may be created empty, e.g., Table(). However, if records is
        not None, then both the ttype and fields must be given.

        .records can be a flat list of values (which will be put into a list
        of lists with each sublist being len(fields) long), or a list of
        lists in which case each list is _assumed_ to be len(fields) i.e.,
        len(tclass.fields), long
        .RecordClass is a dynamically created namedtuple that is used when
        accessing a single record via [] or when iterating a table's
        records.

        comment is an optional str.
        '''
        self.RecordClass = None
        self.tclass = TClass(ttype, fields)
        self.records = []
        self.comment = comment
        if records:
            if not ttype:
                raise Error('#320:can\'t create an unnamed nonempty table')
            if not self.tclass:
                raise Error(
                    '#330:can\'t create a nonempty table without fields')
            if isinstance(records, (list, List)):
                if self.RecordClass is None:
                    self._make_record_class()
                self.records = list(records)
            else:
                for value in records:
                    self.append(value)


    @property
    def ttype(self):
        return self.tclass.ttype


    @property
    def fields(self):
        return self.tclass.fields


    def field(self, column):
        return self.tclass.fields[column]


    @property
    def _next_vtype(self):
        if self.tclass:
            if not self.records:
                return self.tclass.fields[0].vtype
            else:
                if len(self.records[-1]) == len(self.tclass):
                    return self.tclass.fields[0].vtype
                return self.tclass.fields[len(self.records[-1])].vtype


    def append(self, value):
        '''Use to append a value to the table. The value will be added to
        the last row if that isn't full, or as the first value in a new
        row'''
        if self.RecordClass is None:
            self._make_record_class()
        if not self.records or len(self.records[-1]) >= len(self.tclass):
            self.records.append([])
        self.records[-1].append(value)


    @property
    def is_scalar(self):
        for field in self.fields:
            if field.vtype is None:
                break # any type allowed so need to check records themselves
            if field.vtype not in _VALUE_TYPES:
                return False # non-scalar expected so not a scalar table
        else:
            return True # all vtypes specified and all scalar
        for row in self.records:
            for x in row:
                if not is_scalar(x):
                    return False
        return True


    def _make_record_class(self):
        if not self.ttype:
            raise Error('#340:can\'t use an unnamed table')
        if not self.fields:
            raise Error('#350:can\'t create a table with no fields')
        self.RecordClass = collections.namedtuple(
            f'UXF{self.ttype}', # prefix avoids name clashes
            [field.name for field in self.fields])


    def __iadd__(self, value):
        if not self.ttype:
            raise Error('#360:can\'t append to an unnamed table')
        if not self.fields:
            raise Error('#370:can\'t append to a table with no fields')
        if isinstance(value, (list, List, tuple)):
            for v in value:
                self.append(v)
        else:
            self.append(value)
        return self


    def __getitem__(self, row):
        '''Return the row-th record as a namedtuple'''
        try:
            return self.RecordClass(*self.records[row])
        except TypeError as err:
            if 'missing' in str(err):
                err = '#380:table\'s ttype has fewer fields than in a row'
                raise Error(err) from None


    def __iter__(self):
        if self.RecordClass is None:
            self._make_record_class()
        try:
            for record in self.records:
                yield self.RecordClass(*record)
        except TypeError as err:
            if 'missing' in str(err):
                raise Error(
                    '#390:table\'s ttype has fewer fields than in a row')


    def __len__(self):
        return len(self.records)


    def __str__(self):
        parts = [f'ttype={self.ttype!r}']
        if self.fields:
            parts.append(f'fields={self.fields!r}')
        else:
            parts.append('(no fields)')
        if self.comment:
            parts.append(f'comment={self.comment!r}')
        parts.append(f'({len(self.records)} records)')
        return ' '.join(parts)


    def __repr__(self):
        return (f'{self.__class__.__name__}(ttype={self.ttype!r}, '
                f'fields={self.fields!r}, '
                f'records={self.records!r}, comment={self.comment!r})')


def _parse(tokens, filename='-', *, on_error=on_error, _imported=None):
    parser = _Parser(filename, on_error=on_error, _imported=_imported)
    data, comment = parser.parse(tokens)
    return data, comment, parser.tclasses, parser.imports


class _Parser:

    def __init__(self, filename, *, on_error=on_error, _imported=None):
        self.filename = filename
        self.on_error = functools.partial(
            on_error, filename=os.path.basename(filename))
        self.clear()
        if _imported is not None:
            self.imported = _imported
        if filename and filename != '-':
            filename = _full_filename(filename)
            if filename in self.imported:
                self.error(400, f'already imported {filename}', fail=True)
            self.imported.add(filename)


    def error(self, code, message, *, fail=False):
        self.on_error(self.lino, code, message, fail=fail)


    def clear(self):
        self.stack = []
        self.imports = {} # key=ttype value=import text
        self.imported = set() # to avoid reimports or self import
        self.tclasses = {} # key=ttype value=TClass
        self.lino_for_tclass = {} # key=ttype value=lino
        self.used_tclasses = set()
        self.pos = -1
        self.lino = 0


    def parse(self, tokens):
        if not tokens:
            return
        self.tokens = tokens
        data = None
        comment = self._parse_file_comment()
        self._parse_imports()
        self._parse_tclasses()
        for i, token in enumerate(self.tokens):
            self.lino = token.lino
            kind = token.kind
            collection_start = self._is_collection_start(kind)
            if data is None and not collection_start:
                self.error(402,
                           f'expected a map, list, or table, got {token}')
            if collection_start:
                self._on_collection_start(token)
                if data is None:
                    data = self.stack[0]
            elif self._is_collection_end(kind):
                self._on_collection_end(token)
            elif kind is _Kind.COMMENT:
                self._handle_comment(i, token)
            elif kind is _Kind.IDENTIFIER:
                self._handle_identifier(i, token)
            elif kind is _Kind.TYPE:
                self._handle_type(i, token)
            elif kind is _Kind.STR:
                self._handle_str(i, token)
            elif kind.is_scalar:
                self._handle_scalar(i, token)
            elif kind is _Kind.EOF:
                break
            else:
                self.error(410, f'unexpected token, got {token}')
        self._check_tclasses()
        return data, comment


    def _check_tclasses(self):
        imported = set(self.imports.keys())
        defined = set(self.tclasses.keys())
        unused = defined - self.used_tclasses
        unused -= imported # don't warn on unused imports
        if unused:
            self._report_tclasses(unused, 'unused')
        undefined = self.used_tclasses - defined
        if undefined:
            self._report_tclasses(undefined, 'undefined')


    def _report_tclasses(self, tclasses, what):
        diff = sorted(tclasses)
        if len(diff) == 1:
            self.error(416, f'{what} type: {diff[0]!r}')
        else:
            diff = ', '.join(repr(t) for t in diff)
            self.error(418, f'{what} types: {diff}')


    def _handle_comment(self, i, token):
        parent = self.stack[-1]
        prev_token = self.tokens[i - 1]
        if not self._is_collection_start(prev_token.kind):
            self.error(420, 'comments may only be put at the beginning '
                       f'of a map, list, or table, not after {prev_token}')
        parent.comment = token.value


    def _handle_identifier(self, i, token):
        parent = self.stack[-1]
        if (self.tokens[i - 1].kind is _Kind.TYPE and
            (self.tokens[i - 2].kind is _Kind.MAP_BEGIN or
                (self.tokens[i - 2].kind is _Kind.COMMENT and
                 self.tokens[i - 3].kind is _Kind.MAP_BEGIN))):
            tclass = self.tclasses.get(token.value)
            if tclass is None:
                self.error(430, f'undefined map value table type, {token}')
            else:
                parent.vtype = tclass.ttype
                self.used_tclasses.add(tclass.ttype)
        elif self.tokens[i - 1].kind is _Kind.LIST_BEGIN or (
                self.tokens[i - 1].kind is _Kind.COMMENT and
                self.tokens[i - 2].kind is _Kind.LIST_BEGIN):
            vtype = self.tclasses.get(token.value)
            if vtype is None:
                self.error(440, f'undefined list table type, {token}')
            else:
                parent.vtype = vtype.name
                self.used_tclasses.add(vtype.name)
        elif self.tokens[i - 1].kind is _Kind.TABLE_BEGIN or (
                self.tokens[i - 1].kind is _Kind.COMMENT and
                self.tokens[i - 2].kind is _Kind.TABLE_BEGIN):
            tclass = self.tclasses.get(token.value)
            if tclass is None:
                self.error(450, f'undefined table tclass, {token}',
                           fail=True) # A table with no tclass is invalid
            else:
                parent.tclass = tclass
                self.used_tclasses.add(tclass.ttype)
                if len(self.stack) > 1:
                    grand_parent = self.stack[-2]
                    # map or list:
                    vtype = getattr(grand_parent, 'vtype', None)
                    if (vtype is not None and vtype != 'table' and
                            vtype != tclass.ttype):
                        self.error(
                            456, (f'expected table value of type {vtype}, '
                                  f'got value of type {tclass.ttype}'))
        else: # should never happen
            self.error(460, 'ttypes may only appear at the start of a '
                       f'map (as the value type), list, or table, {token}')


    def _handle_type(self, i, token):
        parent = self.stack[-1]
        if isinstance(parent, List):
            if parent.vtype is not None:
                self.error(470, 'can only have at most one vtype for a '
                           f'list, got {token}')
            parent.vtype = token.value
        elif isinstance(parent, Map):
            if parent.ktype is None:
                parent.ktype = token.value
            elif parent.vtype is None:
                parent.vtype = token.value
            else:
                self.error(480, 'can only have at most one ktype and one '
                           f'vtype for a map, got {token}')
        else:
            self.error(490, 'ktypes and vtypes are only allowed at the '
                       f'start of maps and lists, got {token}')


    def _handle_str(self, i, token):
        value = token.value
        for converter in _Converters.values():
            if converter is not None and converter.from_str is not None:
                v, ok = converter.from_str(value)
                if ok:
                    self.stack[-1].append(v)
                    return
        vtype, message = self.typecheck(value)
        if value is not None and vtype is not None and vtype in {
                'bool', 'int', 'real', 'date', 'datetime'}:
            new_value = naturalize(value)
            if new_value != value:
                self.error(492,
                           f'converted str {value!r} to {vtype} {value}')
                value = new_value
            else:
                self.error(494, message)
        self.stack[-1].append(value)


    def _handle_scalar(self, i, token):
        value = token.value
        vtype, message = self.typecheck(value)
        if value is not None and vtype is not None:
            if vtype == 'real' and isinstance(value, int):
                v = float(value)
                self.error(496, f'converted int {value} to real {v}')
                value = v
            elif vtype == 'int' and isinstance(value, float):
                v = round(value)
                self.error(498, f'converted real {value} to int {v}')
                value = v
            else:
                self.error(500, message)
        self.stack[-1].append(value)


    def _on_collection_start(self, token):
        kind = token.kind
        if kind is _Kind.MAP_BEGIN:
            value = Map()
        elif kind is _Kind.LIST_BEGIN:
            value = List()
        elif kind is _Kind.TABLE_BEGIN:
            value = Table()
        else:
            self.error(504, f'expected to create map, list, or table, '
                       f'got {token}')
        if self.stack:
            _, message = self.typecheck(value)
            if message is not None:
                self.error(506, message)
            self.stack[-1].append(value) # add the collection to the parent
        self.stack.append(value) # make the collection the current parent


    def _on_collection_end(self, token):
        if not self.stack:
            self.error(510, f'unexpected {token} suggests unmatched map, '
                       'list, or table start/end pair')
        parent = self.stack[-1]
        if token.kind is _Kind.LIST_END:
            Class = List
            closer = ']'
        elif token.kind is _Kind.MAP_END:
            Class = Map
            closer = '}'
        elif token.kind is _Kind.TABLE_END:
            Class = Table
            closer = ')'
        if not isinstance(parent, Class):
            self.error(512, f'expected {closer!r}, got {token.value!r}')
        self.stack.pop()


    def _is_collection_start(self, kind):
        return kind in {_Kind.MAP_BEGIN, _Kind.LIST_BEGIN,
                        _Kind.TABLE_BEGIN}


    def _is_collection_end(self, kind):
        return kind in {_Kind.MAP_END, _Kind.LIST_END,
                        _Kind.TABLE_END}


    def _parse_file_comment(self):
        if self.tokens:
            token = self.tokens[0]
            self.lino = token.lino
            if token.kind is _Kind.COMMENT:
                self.tokens = self.tokens[1:]
                return token.value
        return None


    def _parse_imports(self):
        offset = 0
        for index, token in enumerate(self.tokens):
            self.lino = token.lino
            if token.kind is _Kind.IMPORT:
                self._handle_import(token.value)
                offset = index + 1
        self.tokens = self.tokens[offset:]


    def _parse_tclasses(self):
        tclass = None
        offset = 0
        for index, token in enumerate(self.tokens):
            self.lino = token.lino
            if token.kind is _Kind.TCLASS_BEGIN:
                if tclass is not None and tclass.ttype is not None:
                    self.tclasses[tclass.ttype] = tclass
                    self.lino_for_tclass[tclass.ttype] = self.lino
                tclass = TClass(None)
            elif token.kind is _Kind.COMMENT:
                tclass.comment = token.value
            elif token.kind is _Kind.IDENTIFIER:
                if tclass.ttype is None:
                    tclass.ttype = token.value
                else:
                    tclass.append(token.value)
            elif token.kind is _Kind.TYPE:
                if not tclass:
                    self.error(520, 'cannot use a built-in type name or '
                               f'constant as a tclass name, got {token}',
                               fail=True)
                else:
                    vtype = token.value
                    tclass.set_vtype(-1, vtype)
            elif token.kind is _Kind.TCLASS_END:
                if tclass is not None and bool(tclass):
                    self.tclasses[tclass.ttype] = tclass
                    if tclass.ttype not in self.lino_for_tclass:
                        self.lino_for_tclass[tclass.ttype] = self.lino
                offset = index + 1
            else:
                break # no TClasses at all
        self.tokens = self.tokens[offset:]


    def _handle_import(self, value):
        filename = text = None
        try:
            if value.startswith(('http://', 'https://')):
                text = self._url_import(value)
            elif '.' not in value: # system import
                filename = self._system_import(value)
            else:
                filename = value
            if filename is not None:
                uxo = self._load_import(filename)
            elif text is not None:
                try:
                    uxo = loads(text, on_error=self._on_import_error,
                                _imported=self.imported)
                except Error as err:
                    self.error(530, f'failed to import {value!r}: {err}')
            else:
                self.error(540, 'there are no ttype definitions to import '
                           f'{value!r} ({filename!r})')
                return # should never get here
            for ttype, tclass in uxo.tclasses.items():
                self.tclasses[ttype] = tclass
                self.imports[ttype] = value
        except _HandleImportError:
            pass # don't reimport & errors already handled


    def _url_import(self, url):
        if url in self.imported:
            raise _HandleImportError # don't reimport
        try:
            with urllib.request.urlopen(url) as file:
                return file.read().decode('utf-8')
        except (UnicodeDecodeError, urllib.error.HTTPError) as err:
            self.error(550, f'failed to import {url!r}: {err}')
            raise _HandleImportError
        finally:
            self.imported.add(url) # don't want to retry


    def _system_import(self, value):
        filename = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                f'{value}.uxf'))
        if os.path.isfile(filename):
            return filename
        self.error(560, 'there is no system ttype definition '
                   f'file {value!r} ({filename!r})')
        raise _HandleImportError


    def _load_import(self, filename):
        path = (os.path.dirname(self.filename) if
                self.filename and self.filename != '-' else '.')
        filename = _full_filename(filename, path)
        if filename in self.imported:
            raise _HandleImportError # don't reimport
        try:
            return load(filename, on_error=self._on_import_error,
                        _imported=self.imported)
        except Error as err:
            if filename in self.imported:
                self.error(580, f'cannot do circular imports {filename!r}',
                           fail=True)
            else:
                self.error(586, f'failed to import {filename!r}: {err}')
            raise _HandleImportError # couldn't import
        finally:
            self.imported.add(filename) # don't want to retry


    def _on_import_error(self, lino, code, message, *, filename, fail=False,
                         verbose=True):
        if code == 418: # we expect all ttypes to be unused here
            return
        self.on_error(lino, code, message, filename=filename, fail=fail,
                      verbose=verbose)


    def typecheck(self, value):
        parent = self.stack[-1]
        if isinstance(parent, Map):
            vtype = parent.ktype if parent._next_is_key else parent.vtype
        elif isinstance(parent, List):
            vtype = parent.vtype
        else: # must be a Table
            vtype = parent._next_vtype
        if value is not None and vtype is not None:
            if vtype in _BUILT_IN_NAMES:
                if not isinstance(value, _TYPECHECK_CLASSES[vtype]):
                    message = (f'expected {vtype}, got '
                               f'{value.__class__.__name__} {value}')
                    return vtype, message
            elif vtype not in self.tclasses:
                message = (f'expected {vtype}, got '
                           f'{value.__class__.__name__} {value}')
                return vtype, message
        return None, None


_TYPECHECK_CLASSES = dict(
    collection=(List, Map, Table), bool=bool, bytes=(bytes, bytearray),
    date=datetime.date, datetime=datetime.datetime, int=int, list=List,
    map=Map, real=float, str=str, table=Table)
_BUILT_IN_NAMES = tuple(_TYPECHECK_CLASSES.keys())


def dump(filename_or_filelike, data, *, indent=2, use_true_false=False,
         on_error=on_error):
    '''
    filename_or_filelike is sys.stdout or a filename or an open writable
    file (text mode UTF-8 encoded). If filename_or_filelike is a filename
    with a .gz suffix then the output will be gzip-compressed.

    data is a Uxf object, or a list, List, dict, Map, or Table, that this
    function will write to the filename_or_filelike in UXF format.

    Set indent to 0 (and use_true_false to True) to minimize the file size.

    If use_true_false is False (the default), bools are output as 'yes' or
    'no'; but if use_true_false is True the are output as 'true' or 'false'.
    '''
    pad = ' ' * indent
    close = False
    if isinstance(filename_or_filelike, (str, pathlib.Path)):
        filename_or_filelike = str(filename_or_filelike)
        opener = (gzip.open if filename_or_filelike[-3:].upper().endswith(
                  '.GZ') else open)
        file = opener(filename_or_filelike, 'wt', encoding=UTF8)
        close = True
    else:
        file = filename_or_filelike
    try:
        if not isinstance(data, Uxf):
            data = Uxf(data)
        _Writer(file, data, pad, use_true_false, on_error)
    finally:
        if close:
            file.close()


def dumps(data, *, indent=2, use_true_false=False, on_error=on_error):
    '''
    data is a Uxf object, or a list, List, dict, Map, or Table that this
    function will write to a string in UXF format which will then be
    returned.

    Set indent to 0 (and use_true_false to True) to minimize the string's
    size.

    If use_true_false is False (the default), bools are output as 'yes' or
    'no'; but if use_true_false is True the are output as 'true' or 'false'.
    '''
    pad = ' ' * indent
    string = io.StringIO()
    if not isinstance(data, Uxf):
        data = Uxf(data)
    _Writer(string, data, pad, use_true_false, on_error)
    return string.getvalue()


class _Writer:

    def __init__(self, file, uxo, pad, use_true_false, on_error):
        self.file = file
        self.yes = 'true' if use_true_false else 'yes'
        self.no = 'false' if use_true_false else 'no'
        self.on_error = on_error
        self.write_header(uxo.custom)
        if uxo.comment is not None:
            self.file.write(f'#<{escape(uxo.comment)}>\n')
        if uxo.imports:
            self.write_imports(uxo.import_filenames)
        if uxo.tclasses:
            self.write_tclasses(uxo.tclasses, uxo.imports)
        if not self.write_value(uxo.data, pad=pad):
            self.file.write('\n')


    def error(self, code, message):
        self.on_error(0, code, message)


    def write_header(self, custom):
        self.file.write(f'uxf {VERSION}')
        if custom:
            self.file.write(f' {custom}')
        self.file.write('\n')


    def write_imports(self, import_filenames):
        for filename in import_filenames: # don't sort!
            self.file.write(f'!{filename}\n')


    def write_tclasses(self, tclasses, imports):
        for ttype, tclass in sorted(tclasses.items()):
            if imports and ttype in imports:
                continue # defined in an import
            self.file.write('=')
            if tclass.comment:
                self.file.write(f'#<{escape(tclass.comment)}> ')
            self.file.write(f'{tclass.ttype}')
            for field in tclass.fields:
                self.file.write(f' {field.name}')
                if field.vtype is not None:
                    self.file.write(f':{field.vtype}')
            self.file.write('\n')


    def write_value(self, item, indent=0, *, pad, is_map_value=False):
        if isinstance(item, (set, frozenset, tuple, collections.deque)):
            item = List(item)
        if isinstance(item, (list, List)):
            return self.write_list(item, indent, pad=pad,
                                   is_map_value=is_map_value)
        if isinstance(item, (dict, Map)):
            return self.write_map(item, indent, pad=pad,
                                  is_map_value=is_map_value)
        if isinstance(item, Table):
            return self.write_table(item, indent, pad=pad,
                                    is_map_value=is_map_value)
        return self.write_scalar(item, indent=indent, pad=pad,
                                 is_map_value=is_map_value)


    def write_list(self, item, indent=0, *, pad, is_map_value=False):
        tab = '' if is_map_value else pad * indent
        prefix = self.collection_prefix(item)
        if len(item) == 0:
            self.file.write(f'{tab}[{prefix}]')
            return False
        self.file.write(f'{tab}[{prefix}')
        if len(item) == 1 or (len(item) <= MAX_LIST_IN_LINE and
                              _are_short_len(*item[:MAX_LIST_IN_LINE + 1])):
            return self._write_short_list(' ' if prefix else '', item)
        return self._write_list(item, indent, pad)


    def _write_short_list(self, sep, item):
        for value in item:
            self.file.write(sep)
            self.write_value(value, pad='')
            sep = ' '
        self.file.write(']')
        return False


    def _write_list(self, item, indent, pad):
        self.file.write('\n')
        indent += 1
        for value in item:
            if not self.write_value(value, indent, pad=pad):
                self.file.write('\n')
        tab = pad * (indent - 1)
        self.file.write(f'{tab}]\n')
        return True


    def write_map(self, item, indent=0, *, pad, is_map_value=False):
        tab = '' if is_map_value else pad * indent
        prefix = self.collection_prefix(item)
        if len(item) == 0:
            self.file.write(f'{tab}{{{prefix}}}')
            return False
        if len(item) == 1:
            return self._write_single_item_map(tab, prefix, item)
        return self._write_map(tab, prefix, item, indent, pad, is_map_value)


    def _write_single_item_map(self, tab, prefix, item):
        self.file.write(f'{tab}{{{prefix}')
        key, value = list(item.items())[0]
        self.write_scalar(key, 1, pad=' ')
        self.file.write(' ')
        if self.write_value(value, 1, pad=' ', is_map_value=True):
            self.file.write(tab)
        self.file.write('}')
        if is_scalar(value):
            return False
        self.file.write('\n')
        return True


    def _write_map(self, tab, prefix, item, indent, pad, is_map_value):
        self.file.write(f'{tab}{{{prefix}\n')
        indent += 1
        for key, value in item.items():
            self.write_scalar(key, indent, pad=pad)
            self.file.write(' ')
            if not self.write_value(value, indent, pad=pad,
                                    is_map_value=True):
                self.file.write('\n')
        tab = pad * (indent - 1)
        self.file.write(f'{tab}}}\n')
        return True


    def write_table(self, item, indent=0, *, pad, is_map_value=False):
        tab = '' if is_map_value else pad * indent
        prefix = self.collection_prefix(item)
        self.file.write(f'{tab}({prefix}')
        if len(item) == 0:
            self.file.write(')')
            return False
        if len(item) == 1:
            return self._write_single_record_table(item[0], is_map_value)
        return self._write_table(tab, item, indent, pad, is_map_value)


    def _write_single_record_table(self, record, is_map_value):
        self.file.write(' ')
        self.write_record(record, is_map_value)
        self.file.write(')')
        return False


    def _write_table(self, tab, item, indent, pad, is_map_value):
        self.file.write('\n')
        indent += 1
        tab = pad * indent
        for record in item:
            self.file.write(tab)
            if not self.write_record(record, is_map_value):
                self.file.write('\n')
        tab = pad * (indent - 1)
        self.file.write(f'{tab})\n')
        return True


    def write_record(self, record, is_map_value):
        sep = ''
        for value in record:
            self.file.write(sep)
            nl = self.write_value(value, 0, pad='',
                                  is_map_value=is_map_value)
            sep = ' '
        return nl


    def write_scalar(self, item, indent=0, *, pad, is_map_value=False):
        if not is_map_value:
            self.file.write(pad * indent)
        converters = _Converters.get(type(item))
        if item is None:
            self.file.write('?')
        elif converters is not None and converters.to_str is not None:
            # must come here because some enums type check as ints!
            value = escape(converters.to_str(item))
            self.file.write(f'<{value}>')
        elif isinstance(item, bool):
            self.file.write(self.yes if item else self.no)
        elif isinstance(item, int):
            self.file.write(str(item))
        elif isinstance(item, float):
            text = str(item)
            if '.' not in text:
                text += '.0'
            self.file.write(text)
        elif isinstance(item, (datetime.date, datetime.datetime)):
            self.file.write(item.isoformat())
        elif isinstance(item, str):
            self.file.write(f'<{escape(item)}>')
        elif isinstance(item, (bytes, bytearray)):
            self.file.write(f'(:{item.hex().upper()}:)')
        else:
            self.file.write(str(item))
            self.error(561, 'wrote unexpected item of type '
                       f'{item.__class__.__name__}: {item!r} as a str; '
                       'consider using uxf.add_converter()')
        return False


    def collection_prefix(self, item):
        comment = getattr(item, 'comment', None)
        ktype = getattr(item, 'ktype', None)
        vtype = getattr(item, 'vtype', None)
        tclass = getattr(item, 'tclass', None)
        parts = []
        if comment is not None:
            parts.append(f'#<{escape(comment)}>')
        if ktype is not None:
            parts.append(ktype)
        if vtype is not None:
            parts.append(vtype)
        if tclass is not None:
            parts.append(tclass.ttype)
        return ' '.join(parts) if parts else ''


def is_scalar(x):
    return x is None or isinstance(
        x, (bool, int, float, datetime.date, datetime.datetime, str, bytes,
            bytearray))


def _is_key_type(x):
    return isinstance(x, (int, datetime.date, datetime.datetime, str,
                          bytes))


def _are_short_len(*items):
    for x in items:
        if isinstance(x, (str, bytes, bytearray)):
            if len(x) > MAX_SHORT_LEN:
                return False
        elif x is not None and not isinstance(
                x, (bool, int, float, datetime.date, datetime.datetime)):
            return False
    return True


def _is_uxf_collection(value):
    return isinstance(value, (List, Map, Table))


def _full_filename(filename, path=None):
    if os.path.isabs(filename):
        return filename
    return os.path.abspath(os.path.join(path or '.', filename))


class _HandleImportError(Exception):
    pass


Converter = collections.namedtuple('Converter', ('to_str', 'from_str'))


_Converters = {}


def add_converter(obj_type, *, to_str=repr, from_str=None):
    '''Use this to register custom types and conversions to and from str's.
    to_str takes a value of obj_type and returns a str
    from_str takes a value of str type and either returns (None, False) or
    (value, True) where value is of type obj_type
    '''
    if obj_type in {bool, int, float, datetime.date, datetime.datetime,
                    str, bytes, bytearray}:
        raise Error(
            '#570: can\'t override default conversions for standard types')
    _Converters[obj_type] = Converter(to_str, from_str or obj_type)


def delete_converter(obj_type):
    del _Converters[obj_type]


def naturalize(s):
    '''Given string s returns True if the string is 't', 'true', 'y', 'yes',
    or False if the string is 'f', 'false', 'n', 'no' (case-insensitive), or
    an int if s holds a parsable int, or a float if s holds a parsable
    float, or a datetime.datetime if s holds a parsable ISO8601 datetime
    string, or a datetime.date if s holds a parsable ISO8601 date string, or
    failing these returns the string s unchanged.
    '''
    u = s.upper()
    if u in {'T', 'TRUE', 'Y', 'YES'}:
        return True
    if u in {'F', 'FALSE', 'N', 'NO'}:
        return False
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            try:
                if 'T' in s:
                    if isoparse is not None:
                        return isoparse(s)
                    return datetime.datetime.fromisoformat(s)
                else:
                    if isoparse is not None:
                        return isoparse(s).date()
                    return datetime.date.fromisoformat(s)
            except ValueError:
                return s


def canonicalize(name, is_table_name=True):
    '''Given a name, returns a name that is a valid table or field name.
    is_table_name must be True (the default) for tables since table names
    have additional constraints. (See uxfconvert.py for uses.)'''
    prefix = 'T_' if is_table_name else 'F_'
    cs = []
    if name[0] == '_' or name[0].isalpha():
        cs.append(name[0])
    else:
        cs.append(prefix)
    for c in name[1:]:
        if c.isspace() or c in '/\\,;:.-':
            if not cs or cs[-1] != '_':
                cs.append('_')
        elif c == '_' or c.isalnum():
            cs.append(c)
    name = ''.join(cs)
    if is_table_name and name in RESERVED_WORDS:
        name = prefix + name
    elif not name:
        name = prefix
    if name == prefix:
        name += str(canonicalize.count)
        canonicalize.count += 1
    return name[:MAX_IDENTIFIER_LEN]
canonicalize.count = 1 # noqa: E305


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] in {'-h', '--help', 'help'}:
        raise SystemExit('''\
usage: uxf.py [-l|--lint] [-iN|--indent=N] \
<infile.uxf[.gz]> [<outfile.uxf[.gz]>]
   or: python3 -m uxf ...same options as above...

If an outfile is specified and ends .gz it will be gzip-compressed.
If outfile is - output will be to stdout.
If you just want linting either don't specify an outfile at all or \
use -l or --lint. Lint errors and fixes go to stderr.

Indent defaults to 2 and accepts a range of 0-8. \
The default is silently used if an out of range value is given.

To get an uncompressed .uxf file run: `uxf.py infile.uxf.gz outfile.uxf` or
simply `gunzip infile.uxf.gz`.

To produce a compressed and compact .uxf file run: \
`uxf.py -i0 infile.uxf outfile.uxf.gz`

Converting uxf to uxf will alphabetically order any ttypes.
However, the order of imports is preserved (with any duplicates removed) \
to allow later imports to override earlier ones.
''')
    indent = 2
    args = sys.argv[1:]
    infile = outfile = None
    lint = None
    for arg in args:
        if arg in {'-l', '--lint'}:
            lint = True
        elif arg.startswith(('-i', '--indent=')):
            if arg[1] == 'i':
                indent = int(arg[2:])
            else:
                indent = int(arg[9:])
            if not 0 <= indent <= 9:
                indent = 2
        elif infile is None:
            infile = arg
        else:
            outfile = arg
    try:
        if (outfile is not None and os.path.abspath(infile) ==
                os.path.abspath(outfile)):
            raise Error('won\'t overwrite {outfile}')
        lint = lint or (lint is None and outfile is None)
        on_error = functools.partial(on_error, verbose=lint,
                                     filename=infile)
        uxo = load(infile, on_error=on_error)
        do_dump = outfile is not None
        outfile = sys.stdout if outfile == '-' else outfile
        on_error = functools.partial(on_error, verbose=lint,
                                     filename=outfile)
        if do_dump:
            dump(outfile, uxo, indent=indent, on_error=on_error)
    except (IOError, Error) as err:
        print(f'uxf.py:error:{err}', file=sys.stderr)
