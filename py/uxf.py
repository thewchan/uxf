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

The uxf module's public API provides the following free functions and
classes.

    load(filename_or_filelike): -> uxo
    loads(uxf_text): -> uxo

These functions read UXF data from a file, file-like, or string.
The returned uxo is of type Uxf (see below).
See the function docs for additional options.

    dump(filename_or_filelike, data)
    dumps(data) -> uxf_text

These functions write UXF data to a file, file-like, or string.
The data can be a Uxf object or a single list, List, dict, Map, or Table.
dump() writes the data to the filename_or_filelike; dumps() writes the data
into a string that's then returned. See the function docs for additional
options.

    add_converter(obj_type, to_str, from_str)

This function can be used to register custom types and custom converters
to/from strings. (See test_converter.py examples of use.)

To have uxf automatically convert tuples, collections.deques, sets, and
frozensets to Lists, set `uxf.AutoConvertSequences = True`.

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

This class is used to propagate errors (and warnings if warn_is_error is
True).

    Uxf

This class has a .data attribute which holds a Map, List, or Table, a
.custom str holding a (possibly empty) custom string, and a .ttypes holding
a (possibly empty) dict whose names are TType table names and whose values
are TTypes. It also has convenience dump() and dumps() methods.

    List

This class is used to represent a UXF list. It is a collections.UserList
subclass that also has .comment and .vtype attributes.

    Map

This class is used to represent a UXF map. It is a collections.UserDict
subclass that also has .comment, .ktype, and .vtype attributes. It also has
a special append() method.

    Table

This class is used to store UXF Tables. A Table has a TType (see below) and
a records list which is a list of lists of scalars with each sublist having
the same number of items as the number of fields. It also has .comment and
.ttype attributes and a special append() method.

    TType

This class is used to store a Table's name and fields (see below).

    Field

This class is used to store a Table's fields. The .name must start with a
letter and be followed by 0-uxf.MAX_IDENTIFIER_LEN-1 letters, digits, or
underscores..vtype must be one of these strs: 'bool', 'int', 'real', 'date',
'datetime', 'str', 'bytes', or None (which means accept any valid type).

Note that the __version__ is the module version (i.e., the versio of this
implementation), while the VERSION is the maximum UXF version that this
module can read (and the UXF version that it writes).
'''

import collections
import datetime
import enum
import gzip
import io
import pathlib
import sys
from xml.sax.saxutils import escape, unescape

try:
    from dateutil.parser import isoparse
except ImportError:
    isoparse = None


__all__ = ('__version__', 'VERSION', 'load', 'loads', 'dump', 'dumps',
           'naturalize', 'canonicalize', 'is_scalar', 'Uxf', 'List',
           'Map', 'Table', 'TType', 'Field')
__version__ = '0.25.0' # uxf module version
VERSION = 1.0 # uxf file format version

AutoConvertSequences = False

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
TYPENAMES = frozenset(_ANY_VALUE_TYPES | {'null'})
_MISSING = object()


class Uxf:
    '''A Uxf object holds three attributes.

    .data is a List, Map, or Table of data
    .custom is an opional custom string used for customizing the file format
    .ttypes is a dict where each key is a ttype name and each value is a
    TType object.
    .comment is an optional file-level comment
    '''

    def __init__(self, data=None, *, custom='', ttypes=None, comment=None):
        '''data may be a list, List, dict, Map, or Table and will default to
        a List if not specified; if given ttypes must be a dict whose values
        are TTypes and whose corresponding keys are the TTypes' names; if
        given the comment is a file-level comment that follows the uxf
        header and precedes any TTypes and data'''
        self.data = data
        self.custom = custom
        self.comment = comment
        self.ttypes = ttypes if ttypes is not None else {}


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
        if not _is_uxf_collection(data):
            raise Error('#800:Uxf data must be a list, List, dict, Map, or '
                        f'Table, got {type(data)}')
        self._data = data


    def dump(self, filename_or_filelike, *, indent=2, use_true_false=False,
             warn_is_error=False):
        '''Convenience method that wraps the module-level dump() function'''
        dump(filename_or_filelike, self, indent=indent,
             use_true_false=use_true_false, warn_is_error=warn_is_error)


    def dumps(self, *, indent=2, use_true_false=False,
              warn_is_error=False):
        '''Convenience method that wraps the module-level dumps()
        function'''
        return dumps(self, indent=indent, use_true_false=use_true_false,
                     warn_is_error=warn_is_error)


    def typecheck(self, fixtypes=False):
        _typecheck(self.data, 'collection', ttypes=self.ttypes)
        self.data.typecheck(self.ttypes, fixtypes=fixtypes)


def load(filename_or_filelike, *, check=False, fixtypes=False,
         warn_is_error=False):
    '''
    Returns a Uxf object.

    filename_or_filelike is sys.stdin or a filename or an open readable file
    (text mode UTF-8 encoded, optionally gzipped).

    If warn_is_error is True warnings raise Error exceptions.
    '''
    filename = (filename_or_filelike if isinstance(filename_or_filelike,
                (str, pathlib.Path)) else '-')
    return _loads(_read_text(filename_or_filelike), check=check,
                  fixtypes=fixtypes, warn_is_error=warn_is_error,
                  filename=filename)


def loads(uxf_text, *, check=False, fixtypes=False, warn_is_error=False):
    '''
    Returns a Uxf object.

    uxf_text must be a string of UXF data.

    If warn_is_error is True warnings raise Error exceptions.
    '''
    return _loads(uxf_text, check=check, fixtypes=fixtypes,
                  warn_is_error=warn_is_error)


def _loads(uxf_text, *, check=False, fixtypes=False, warn_is_error=False,
           filename='-'):
    tokens, custom, text = _tokenize(uxf_text, warn_is_error=warn_is_error,
                                     filename=filename)
    data, comment, ttypes = _parse(
        tokens, text=uxf_text, warn_is_error=warn_is_error,
        filename=filename)
    uxo = Uxf(data, custom=custom, ttypes=ttypes, comment=comment)
    if check:
        uxo.typecheck(fixtypes=fixtypes)
    return uxo


def _tokenize(uxf_text, *, warn_is_error=False, filename='-'):
    lexer = _Lexer(warn_is_error=warn_is_error, filename=filename)
    tokens = lexer.tokenize(uxf_text)
    return tokens, lexer.custom, uxf_text


def _read_text(filename_or_filelike):
    if not isinstance(filename_or_filelike, (str, pathlib.Path)):
        return filename_or_filelike.read()
    try:
        with gzip.open(filename_or_filelike, 'rt', encoding=UTF8) as file:
            return file.read()
    except gzip.BadGzipFile:
        with open(filename_or_filelike, 'rt', encoding=UTF8) as file:
            return file.read()


class _ErrorMixin:

    __slots__ = ()

    def warn(self, code, message):
        if self.warn_is_error:
            self.error(code, message)
        lino = self.text.count('\n', 0, self.pos) + 1
        print(f'Warning:#{code}:{self.filename}:{lino}: {message}')


    def error(self, code, message):
        lino = self.text.count('\n', 0, self.pos) + 1
        raise Error(f'#{code}:{self.filename}:{lino}: {message}')


class _Lexer(_ErrorMixin):

    def __init__(self, *, warn_is_error=False, filename='-'):
        self.warn_is_error = warn_is_error
        self.filename = filename


    def clear(self):
        self.pos = 0 # current
        self.custom = None
        self.in_ttype = False
        self.tokens = []


    def tokenize(self, text):
        self.clear()
        self.text = text
        self.scan_header()
        self.maybe_read_comment()
        while not self.at_end():
            self.scan_next()
        self.add_token(_Kind.EOF)
        return self.tokens


    def scan_header(self):
        i = self.text.find('\n')
        if i == -1:
            self.error(100, 'missing UXF file header or empty file')
        self.pos = i
        parts = self.text[:i].split(None, 2)
        if len(parts) < 2:
            self.error(110, 'invalid UXF file header')
        if parts[0] != 'uxf':
            self.error(120, 'not a UXF file')
        try:
            version = float(parts[1])
            if version > VERSION:
                self.warn(131, f'version ({version}) > current ({VERSION})')
        except ValueError:
            self.warn(141, 'failed to read UXF file version number')
        if len(parts) > 2:
            self.custom = parts[2]


    def maybe_read_comment(self):
        self.skip_ws()
        if not self.at_end() and self.text[self.pos] == '#':
            self.pos += 1 # skip the #
            if self.peek() == '<':
                self.pos += 1 # skip the leading <
                value = self.match_to(
                    '>', error_text='unterminated comment string')
                self.add_token(_Kind.COMMENT, unescape(value))
            else:
                self.error(150, 'invalid comment syntax: expected \'<\', '
                           f'got {self.peek()}')


    def at_end(self):
        return self.pos >= len(self.text)


    def scan_next(self):
        c = self.getch()
        if c.isspace():
            pass # ignore insignificant whitespace
        elif c == '(':
            if self.peek() == ':':
                self.pos += 1
                self.read_bytes()
            else:
                self.check_in_ttype()
                self.add_token(_Kind.TABLE_BEGIN)
        elif c == ')':
            self.add_token(_Kind.TABLE_END)
        elif c == '[':
            self.check_in_ttype()
            self.add_token(_Kind.LIST_BEGIN)
        elif c == '=':
            self.add_token(_Kind.TTYPE_BEGIN)
            self.in_ttype = True
        elif c == ']':
            self.add_token(_Kind.LIST_END)
        elif c == '{':
            self.check_in_ttype()
            self.add_token(_Kind.MAP_BEGIN)
        elif c == '}':
            self.in_ttype = False
            self.add_token(_Kind.MAP_END)
        elif c == '?':
            self.add_token(_Kind.NULL)
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
            self.error(160, f'invalid character encountered: {c!r}')


    def check_in_ttype(self):
        if self.in_ttype:
            self.in_ttype = False
            self.add_token(_Kind.TTYPE_END)


    def read_comment(self):
        if self.tokens and self.tokens[-1].kind in {
                _Kind.LIST_BEGIN, _Kind.MAP_BEGIN, _Kind.TABLE_BEGIN,
                _Kind.TTYPE_BEGIN}:
            if self.peek() != '<':
                self.error(170, 'a str must follow the # comment '
                           f'introducer, got {self.peek()!r}')
            self.pos += 1 # skip the leading <
            value = self.match_to('>',
                                  error_text='unterminated comment string')
            self.add_token(_Kind.COMMENT, unescape(value))
        else:
            self.error(180, 'comments may only occur at the start of '
                       'TTypes, Maps, Lists, and Tables')


    def read_string(self):
        value = self.match_to('>', error_text='unterminated string')
        self.add_token(_Kind.STR, unescape(value))


    def read_bytes(self):
        value = self.match_to(':)', error_text='unterminated bytes')
        try:
            self.add_token(_Kind.BYTES, bytes.fromhex(value))
        except ValueError as err:
            self.error(190, f'expected bytes, got {value!r}: {err}')


    def read_negative_number(self, c):
        is_real = False
        start = self.pos - 1
        while not self.at_end() and (c in '.eE' or c.isdecimal()):
            if c in '.eE':
                is_real = True
            c = self.text[self.pos]
            self.pos += 1
        convert = float if is_real else int
        text = self.text[start:self.pos]
        try:
            value = convert(text)
            self.add_token(_Kind.REAL if is_real else _Kind.INT, -value)
        except ValueError as err:
            self.error(200, f'invalid number: {text}: {err}')


    def read_positive_number_or_date(self, c):
        start = self.pos - 1
        is_real, is_datetime, hyphens = self.read_number_or_date_chars(c)
        self.pos -= 1 # wind back to terminating non-numeric non-date char
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
                self.error(210,
                           f'invalid number or date/time: {text}: {err}')


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
            self.warn(221, f'skipped timezone data, used {text[:19]!r}, '
                      f'got {text!r}')
        except ValueError as err:
            self.error(230, f'invalid datetime: {text}: {err}')


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
            self.error(240, f'expected const or identifier, got {text!r}')


    def read_field_vtype(self):
        self.skip_ws()
        identifier = self.match_identifier(self.pos, 'field vtype')
        self.add_token(_Kind.TYPE, identifier)


    def peek(self):
        return '\0' if self.at_end() else self.text[self.pos]


    def skip_ws(self):
        while self.pos < len(self.text) and self.text[self.pos].isspace():
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
        self.error(250, f'expected {what}, got {text}…')


    def match_to(self, target, *, error_text):
        if not self.at_end():
            i = self.text.find(target, self.pos)
            if i > -1:
                text = self.text[self.pos:i]
                self.pos = i + len(target) # skip past target
                return text
        self.error(260, error_text)


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
        self.tokens.append(_Token(kind, value, self.pos))


class Error(Exception):
    pass


class _Token:

    def __init__(self, kind, value=None, pos=-1):
        self.kind = kind
        self.value = value # literal, i.e., correctly typed item
        self.pos = pos


    def __str__(self):
        parts = [self.kind.name]
        if self.value is not None:
            parts.append(f'={self.value!r}')
        return ''.join(parts)


    def __repr__(self):
        parts = [f'{self.__class__.__name__}({self.kind.name}']
        if self.value is not None:
            parts.append(f', {self.value!r}')
        parts.append(')')
        return ''.join(parts)


@enum.unique
class _Kind(enum.Enum):
    TTYPE_BEGIN = enum.auto()
    TTYPE_END = enum.auto()
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


class List(collections.UserList, _ErrorMixin):

    def __init__(self, *args, **kwargs):
        '''Takes same arguments as list.
        .data holds the actual list
        .comment holds an optional comment
        .vtype holds a UXF type name ('int', 'real', …)'''
        super().__init__(*args, **kwargs)
        self.comment = None
        self.vtype = None


    def typecheck(self, ttypes, *, fixtypes=False):
        for i in range(len(self.data)):
            value = self.data[i]
            check = _typecheck(value, self.vtype, ttypes=ttypes,
                               fixtypes=fixtypes)
            if check.fixed:
                value = check.value
                self.data[i] = value
            if _is_uxf_collection(value):
                value.typecheck(ttypes, fixtypes=fixtypes)


class Map(collections.UserDict, _ErrorMixin):

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
                    raise Error(f'#810:{prefix}a Table ( … ), maybe bytes '
                                '(: … :) was intended?')
                else:
                    raise Error(
                        f'#820:{prefix}{value!r} of type {type(value)}')
            self._pending_key = value
        else:
            self.data[self._pending_key] = value
            self._pending_key = _MISSING


    def typecheck(self, ttypes, *, fixtypes=False):
        keys = list(self.keys())
        for key in keys:
            value = self[key]
            check = _typecheck(key, self.ktype, ttypes=ttypes,
                               fixtypes=fixtypes)
            if check.fixed: # unlikely
                del self[key]
                key = check.value
                self[key] = value
            check = _typecheck(value, self.vtype, ttypes=ttypes,
                               fixtypes=fixtypes)
            if check.fixed:
                value = check.value
                self[key] = value
            if _is_uxf_collection(value):
                value.typecheck(ttypes, fixtypes=fixtypes)


class _CheckNameMixin:

    __slots__ = ()

    def _check_name(self, name):
        if name[0].isdigit():
            raise Error('#830:names must start with a letter or '
                        f'underscore, got {name}')
        for c in name[1:]:
            if not (c == '_' or c.isalnum()):
                raise Error('#840:names may only contain letters, digits, '
                            f'or underscores, got {name}')


class TType(_CheckNameMixin):

    def __init__(self, name, fields=None, *, comment=None):
        '''The type of a Table
        .name holds the ttype's name (equivalent to a vtype or ktype name,
        but always starting with a captital letter)
        .fields holds a list of field names or of fields of type Field
        .comment holds an optional comment'''
        self.name = name
        self.fields = []
        self.comment = comment
        if fields is not None:
            for field in fields:
                if isinstance(field, str):
                    self.fields.append(Field(field))
                else:
                    self.fields.append(field)


    @property
    def name(self):
        return self._name


    @name.setter
    def name(self, name):
        if name is not None:
            self._check_name(name)
        self._name = name


    def append(self, name_or_field, vtype=None):
        if isinstance(name_or_field, Field):
            self.fields.append(name_or_field)
        else:
            self.fields.append(Field(name_or_field, vtype))


    def set_vtype(self, index, vtype):
        self.fields[index].vtype = vtype


    def __bool__(self):
        return bool(self.name) and bool(self.fields)


    def __hash__(self):
        return hash(self.name)


    def __lt__(self, other):
        return self.name < other.name


    def __len__(self):
        return len(self.fields)


    def __repr__(self):
        fields = ', '.join(repr(field) for field in self.fields)
        return (f'{self.__class__.__name__}({self.name!r}, {fields}, '
                f'comment={self.comment!r})')


class Field(_CheckNameMixin):

    def __init__(self, name, vtype=None):
        '''The type of one field in a Table
        .name holds the field's name (equivalent to a vtype or ktype name,
        but always starting with a captital letter)
        .vtype holds a UXF type name ('int', 'real', …)'''
        self.name = name
        self.vtype = vtype


    @property
    def name(self):
        return self._name


    @name.setter
    def name(self, name):
        self._check_name(name)
        self._name = name


    def __repr__(self):
        return f'{self.__class__.__name__}({self.name!r}, {self.vtype!r})'


class Table(_ErrorMixin):
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

    def __init__(self, *, name=None, fields=None, records=None,
                 comment=None):
        '''
        A Table may be created empty, e.g., Table(). However, if records is
        not None, then both the name and fields must be given.

        .records can be a flat list of values (which will be put into a list
        of lists with each sublist being len(fields) long), or a list of
        lists in which case each list is _assumed_ to be len(fields) i.e.,
        len(ttype.fields), long
        .RecordClass is a dynamically created namedtuple that is used when
        accessing a single record via [] or when iterating a table's
        records.

        comment is an optional str.
        '''
        self.RecordClass = None
        self.ttype = TType(name, fields)
        self.records = []
        self.comment = comment
        if records:
            if not name:
                raise Error('#850:can\'t create an unnamed nonempty table')
            if not self.ttype:
                raise Error(
                    '#860:can\'t create a nonempty table without fields')
            if isinstance(records, (list, List)):
                if self.RecordClass is None:
                    self._make_record_class()
                self.records = list(records)
            else:
                for value in records:
                    self.append(value)


    @property
    def name(self):
        return self.ttype.name


    @name.setter
    def name(self, name):
        self.ttype.name = name


    @property
    def fields(self):
        return self.ttype.fields


    def field(self, column):
        return self.ttype.fields[column]


    def append(self, value):
        '''Use to append a value to the table. The value will be added to
        the last row if that isn't full, or as the first value in a new
        row'''
        if self.RecordClass is None:
            self._make_record_class()
        if not self.records or len(self.records[-1]) >= len(self.ttype):
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


    def typecheck(self, ttypes, *, fixtypes=False):
        for row in range(len(self.records)):
            columns = len(self.records[row])
            if columns != len(self.fields):
                print(f'Typecheck:#800:expected {len(self.fields)} fields, '
                      f'got {columns}')
            for column in range(columns):
                if column < len(self.fields):
                    field = self.field(column)
                    value = self.records[row][column]
                    check = _typecheck(value, field.vtype, ttypes=ttypes,
                                       fixtypes=fixtypes)
                    if check.fixed:
                        value = check.value
                        self.records[row][column] = value
                    if _is_uxf_collection(value):
                        value.typecheck(ttypes, fixtypes=fixtypes)


    def _make_record_class(self):
        if not self.name:
            raise Error('#870:can\'t use an unnamed table')
        if not self.fields:
            raise Error('#880:can\'t create a table with no fields')
        self.RecordClass = collections.namedtuple(
            f'UXF{self.name}', # prefix avoids name clashes
            [field.name for field in self.fields])


    def __iadd__(self, value):
        if not self.name:
            raise Error('#890:can\'t append to an unnamed table')
        if not self.fields:
            raise Error('#900:can\'t append to a table with no fields')
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
                err = '#910:table\'s ttype has fewer fields than in a row'
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
                    '#920:table\'s ttype has fewer fields than in a row')


    def __len__(self):
        return len(self.records)


    def __str__(self):
        return (f'Table {self.name!r} {self.fields!r} with '
                f'{len(self.records)} records #{self.comment!r}')


    def __repr__(self):
        return (f'{self.__class__.__name__}(name={self.name!r}, '
                f'fields={self.fields!r}, '
                f'records={self.records!r}, comment={self.comment!r})')


def _parse(tokens, *, text, warn_is_error=False, filename='-'):
    parser = _Parser(warn_is_error=warn_is_error, filename=filename)
    data, comment = parser.parse(tokens, text)
    ttypes = parser.ttypes
    return data, comment, ttypes


class _Parser(_ErrorMixin):

    def __init__(self, *, warn_is_error=False, filename='-'):
        self.warn_is_error = warn_is_error
        self.filename = filename


    def clear(self):
        self.stack = []
        self.ttypes = {}
        self.pos = -1


    def parse(self, tokens, text):
        self.clear()
        if not tokens:
            return
        self.tokens = tokens
        self.text = text
        data = None
        comment = self._parse_file_comment()
        self._parse_ttypes()
        for i, token in enumerate(self.tokens):
            kind = token.kind
            collection_start = self._is_collection_start(kind)
            if data is None and not collection_start:
                self.error(400,
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
                self._handle_string(i, token)
            elif kind.is_scalar:
                self.stack[-1].append(token.value)
            elif kind is _Kind.EOF:
                break
            else:
                self.error(410, f'unexpected token, got {token}')
        return data, comment


    def _handle_comment(self, i, token):
        parent = self.stack[-1]
        prev_token = self.tokens[i - 1]
        if not self._is_collection_start(prev_token.kind):
            self.error(420, 'comments may only be put at the beginning '
                       f'of a map, list, or table, not after {prev_token}')
        parent.comment = token.value


    def _handle_identifier(self, i, token):
        parent = self.stack[-1]
        if not isinstance(parent, Table):
            self.error(430, 'ttype name may only appear at the start of a '
                       f'table, {token}')
        if self.tokens[i - 1].kind is _Kind.TABLE_BEGIN or (
                self.tokens[i - 1].kind is _Kind.COMMENT and
                self.tokens[i - 2].kind is _Kind.TABLE_BEGIN):
            ttype = self.ttypes.get(token.value)
            if ttype is None:
                self.error(440, f'undefined table ttype, {token}')
            parent.ttype = ttype
        else: # should never happen
            self.error(450, 'ttype name may only appear at the start of a '
                       f'table, {token}')


    def _handle_type(self, i, token):
        parent = self.stack[-1]
        if isinstance(parent, List):
            if parent.vtype is not None:
                self.error(460, 'can only have at most one vtype for a '
                           f'list, got {token}')
            parent.vtype = token.value
        elif isinstance(parent, Map):
            if parent.ktype is None:
                parent.ktype = token.value
            elif parent.vtype is None:
                parent.vtype = token.value
            else:
                self.error(470, 'can only have at most one ktype and one '
                           f'vtype for a map, got {token}')
        else:
            self.error(480, 'ktypes and vtypes are only allowed at the '
                       f'start of maps and lists, got {token}')


    def _handle_string(self, i, token):
        value = token.value
        for converters in _Converters.values():
            if converters.from_str is not None:
                new_value, ok = converters.from_str(value)
                if ok:
                    value = new_value
                    break
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
            self.error(
                490, f'expected to create map, list, or table, got {token}')
        if self.stack:
            self.stack[-1].append(value) # add the collection to the parent
        self.stack.append(value) # make the collection the current parent


    def _on_collection_end(self, token):
        if not self.stack:
            self.error(500, f'unexpected {token} suggests unmatched map, '
                       'list, or table start/end pair')
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
            if token.kind is _Kind.COMMENT:
                self.tokens = self.tokens[1:]
                return token.value
        return None


    def _parse_ttypes(self):
        used = self._read_ttypes()
        self._check_used_ttypes(used)


    def _read_ttypes(self):
        used = set()
        ttype = None
        for index, token in enumerate(self.tokens):
            if token.kind is _Kind.TTYPE_BEGIN:
                if ttype is not None and ttype.name is not None:
                    self.ttypes[ttype.name] = ttype
                ttype = TType(None)
            elif token.kind is _Kind.COMMENT:
                ttype.comment = token.value
            elif token.kind is _Kind.IDENTIFIER:
                if ttype.name is None:
                    ttype.name = token.value
                else:
                    ttype.append(token.value)
            elif token.kind is _Kind.TYPE:
                if len(ttype) > 0:
                    vtype = token.value
                    ttype.set_vtype(-1, vtype)
                    if vtype not in TYPENAMES:
                        used.add(vtype)
                else:
                    self.error(
                        510,
                        f'encountered type without field name: {token}')
            elif token.kind is _Kind.TTYPE_END:
                if ttype is not None and bool(ttype):
                    self.ttypes[ttype.name] = ttype
                self.tokens = self.tokens[index + 1:]
            else:
                break # no TTypes at all
        return used


    def _check_used_ttypes(self, used):
        if self.ttypes: # Check that all ttypes referred to are defined
            diff = used - set(self.ttypes.keys())
            if diff:
                diff = sorted(diff)
                if len(diff) == 1:
                    self.error(520,
                               f'ttype uses undefined type: {diff[0]!r}')
                else:
                    diff = ', '.join(repr(t) for t in diff)
                    self.error(530, f'ttype uses undefined types: {diff}')


def dump(filename_or_filelike, data, *, indent=2, use_true_false=False,
         warn_is_error=False):
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
        _Writer(file, data, pad, use_true_false, warn_is_error)
    finally:
        if close:
            file.close()


def dumps(data, *, indent=2, use_true_false=False, warn_is_error=False):
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
    _Writer(string, data, pad, use_true_false, warn_is_error)
    return string.getvalue()


class _Writer:

    def __init__(self, file, uxo, pad, use_true_false, warn_is_error):
        self.file = file
        self.yes = 'true' if use_true_false else 'yes'
        self.no = 'false' if use_true_false else 'no'
        self.warn_is_error = warn_is_error
        self.write_header(uxo.custom)
        if uxo.comment is not None:
            self.file.write(f'#<{escape(uxo.comment)}>\n')
        if uxo.ttypes:
            self.write_ttypes(uxo.ttypes)
        if not self.write_value(uxo.data, pad=pad):
            self.file.write('\n')


    def write_header(self, custom):
        self.file.write(f'uxf {VERSION}')
        if custom:
            self.file.write(f' {custom}')
        self.file.write('\n')


    def write_ttypes(self, ttypes):
        for ttype in sorted(ttypes.values()):
            self.file.write('=')
            if ttype.comment:
                self.file.write(f' #<{escape(ttype.comment)}>')
            self.file.write(f' {ttype.name}')
            for field in ttype.fields:
                self.file.write(f' {field.name}')
                if field.vtype is not None:
                    self.file.write(f':{field.vtype}')
            self.file.write('\n')


    def write_value(self, item, indent=0, *, pad, is_map_value=False):
        if isinstance(item, (set, frozenset, tuple, collections.deque)):
            if AutoConvertSequences:
                item = List(item)
            else:
                raise Error(f'#700:got {item} of type {type(item)}; '
                            'try converting it to a List or '
                            'uxf.AutoConvertSequences = True')
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
        elif isinstance(item, (int, float)):
            self.file.write(str(item))
        elif isinstance(item, (datetime.date, datetime.datetime)):
            self.file.write(item.isoformat())
        elif isinstance(item, str):
            self.file.write(f'<{escape(item)}>')
        elif isinstance(item, (bytes, bytearray)):
            self.file.write(f'(:{item.hex().upper()}:)')
        else:
            message = ('#720:ignoring unexpected item of type '
                       f'{type(item)}: {item!r}; consider using '
                       'uxf.add_converter()')
            if self.warn_is_error:
                raise Error(message)
            print(f'Warning:{message}', file=sys.stderr)
        return False


    def collection_prefix(self, item):
        comment = getattr(item, 'comment', None)
        ktype = getattr(item, 'ktype', None)
        vtype = getattr(item, 'vtype', None)
        ttype = getattr(item, 'ttype', None)
        parts = []
        if comment is not None:
            parts.append(f' #<{escape(comment)}>')
        if ktype is not None:
            parts.append(ktype)
        if vtype is not None:
            parts.append(vtype)
        if ttype is not None:
            parts.append(ttype.name)
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


Converter = collections.namedtuple('Converter', ('to_str', 'from_str'))


_Converters = {}


def add_converter(obj_type, *, to_str=repr, from_str=None):
    'Use this to register custom types and conversions to and from str\'s.'
    if isinstance(obj_type, (bool, int, float, datetime.date,
                             datetime.datetime, str, bytes, bytearray)):
        raise Error(
            '#808: can\'t override default conversions for standard types')
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
    if is_table_name and name in TYPENAMES:
        name = prefix + name
    elif not name:
        name = prefix
    if name == prefix:
        name += str(canonicalize.count)
        canonicalize.count += 1
    return name[:MAX_IDENTIFIER_LEN]
canonicalize.count = 1 # noqa: E305


def _typecheck(value, vtype, *, ttypes=None, fixtypes=False):
    if value is None or not vtype: # null is always a valid value
        return _Typecheck(value, False, True)
    if isinstance(value, Table):
        reply = _typecheck_table(value, vtype, ttypes, fixtypes)
        if reply is not None:
            return reply
    classes = _TYPECHECK_CLASSES.get(vtype)
    if (not isinstance(value, classes) and fixtypes and
            vtype != 'collection'):
        if isinstance(value, str) and vtype in {'bool', 'int', 'real',
                                                'date', 'datetime'}:
            new_value = naturalize(value)
            return _Typecheck(new_value, isinstance(new_value, classes),
                              True)
        if isinstance(value, int) and vtype == 'real':
            return _Typecheck(float(value), True, True)
        if isinstance(value, float) and vtype == 'int':
            return _Typecheck(int(value), True, True)
    if isinstance(value, classes):
        return _Typecheck(value, False, True)
    atype = _TYPECHECK_ATYPES.get(type(value))
    print(f'Typecheck:#810:expected a {vtype}, got {atype}')
    return _Typecheck(value, False, False)


def _typecheck_table(value, vtype, ttypes, fixtypes):
    if vtype == 'collection':
        return _Typecheck(value, False, True) # any collection is ok
    if ttypes is None:
        print(
            f'Typecheck:#820:got table of unknown type {value.ttype.name}')
        return _Typecheck(value, False, False)
    ttype = ttypes.get(value.ttype.name)
    if vtype == ttype.name:
        return _Typecheck(value, False, True)
    else:
        print(f'Typecheck:#822:expected a table of type {vtype}, got '
              f'{value.ttype.name}')
        return _Typecheck(value, False, False)


_Typecheck = collections.namedtuple('_Typecheck', 'value fixed ok')

_TYPECHECK_CLASSES = dict(
    collection=(List, Map, Table), bool=bool, bytes=(bytes, bytearray),
    date=datetime.date, datetime=datetime.datetime, int=int, list=List,
    map=Map, real=float, str=str, table=Table)
_TYPECHECK_ATYPES = {
    bool: 'bool', bytearray: 'bytes', bytes: 'bytes',
    datetime.date: 'date', datetime.datetime: 'datetime', float: 'real',
    int: 'int', List: 'list', Map: 'map', str: 'str', Table: 'table',
    type(None): '?'}


if __name__ == '__main__':
    import os

    if len(sys.argv) < 2 or sys.argv[1] in {'-h', '--help', 'help'}:
        raise SystemExit('''\
usage: uxf.py \
[-c|--check] [-f|--fix-types] [-w|--warn-is-error] [-iN|--indent=N] \
<infile.uxf[.gz]> [<outfile.uxf[.gz]>]
   or: python3 -m uxf ...same options as above...

If check is set any given types are checked against the actual \
values and warnings given if appropriate.
If fixtypes is set mistyped values are correctly typed where possible \
(e.g., int ↔ float, str → date, etc.). If fixtypes is set then check is \
automatically set too.
If warn-is-error is set warnings are treated as errors \
(i.e., the program will terminate with the first error or warning message).
If an outfile is specified and ends .gz it will be gzip-compressed.
Indent defaults to 2 and accepts a range of 0-8. \
The default is silently used if an out of range value is given.

To get an uncompressed .uxf file run: `uxf.py infile.uxf.gz outfile.uxf` or
simply `gunzip infile.uxf.gz`.

To produce a compressed and compact .uxf file run: \
`uxf.py -i0 infile.uxf outfile.uxf.gz`

Converting uxf to uxf will alphabetically order any ttypes.
''')
    check = False
    fixtypes = False
    warn_is_error = False
    indent = 2
    args = sys.argv[1:]
    infile = outfile = None
    for arg in args:
        if arg in {'-c', '--check'}:
            check = True
        elif arg in {'-f', '--fix-types'}:
            fixtypes = True
            check = True
        elif arg in {'-w', '--warn-is-error'}:
            warn_is_error = True
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
        uxo = load(infile, warn_is_error=warn_is_error)
        if check:
            uxo.typecheck(fixtypes=fixtypes)
        outfile = sys.stdout if outfile is None else outfile
        dump(outfile, uxo, indent=indent)
    except (FileNotFoundError, Error) as err:
        print(f'Error:{err}')
