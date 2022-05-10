#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import datetime
import os
import sys
from xml.sax.saxutils import unescape

import uxf

try:
    from dateutil.parser import isoparse
except ImportError:
    isoparse = None


_Kind = uxf._Kind


def main():
    if len(sys.argv) < 2 or sys.argv[1] in {'-h', '--help'}:
        raise SystemExit('''\
usage: uxflint.py [-q|--quiet] <infile> [outfile]
If an outfile is specified (or - for stdout) the infile is saved to it \
with the following fixes:
- the format is standardized (just like using uxf.py infile outfile)
- unused ttypes are removed
- strings are natualized (i.e., converted to bool, int, real, date, or
  datetime where required and where possible)
- ints are converted to reals and vice versa where required
''')
    quiet = False
    infile = outfile = None
    for arg in sys.argv[1:]:
        if arg in {'-q', '--quiet'}:
            quiet = True
        elif infile is None:
            infile = arg
        elif outfile is None:
            outfile = arg
    if outfile is not None and (os.path.abspath(infile) ==
                                os.path.abspath(outfile)):
        raise SystemExit(f'won\'t overwite {infile}')
    uxf.AutoConvertSequences = True
    lexer = _Lexer(infile, verbose=not quiet)
    tokens = lexer.tokenize()
    data, comment, ttypes, errors, fixes = _parse(tokens, filename=infile,
                                                  verbose=not quiet)
    errors += lexer.errors
    fixes += lexer.fixes
    if outfile is not None:
        uxo = uxf.Uxf(data, custom=lexer.custom, ttypes=ttypes,
                      comment=comment)
        if outfile == '-':
            print(uxo.dumps())
        else:
            uxo.dump(outfile)
            if not quiet:
                explained = explain(errors, fixes)
                print(f'saved {outfile!r}: {explained}')
    elif not quiet:
        explained = explain(errors, fixes, 'could have ')
        print(explained)


def explain(errors, fixes, prefix=''):
    if fixes > errors:
        raise SystemExit('internal error') # should never happen
    if errors == 0:
        return 'no errors found'
    if errors == fixes == 1:
        return f'{prefix}found and fixed one error'
    if errors == 1:
        fixes = 'and fixed it' if fixes == 1 else 'but could not fix it'
        return f'{prefix}found one error {fixes}'
    fixes = 'none' if fixes == 0 else 'one' if fixes == 1 else f'{fixes:,}'
    return f'{prefix}found {errors:,} errors and fixed {fixes} of them'


def _error(filename, lino, code, message, *, fail=False, verbose=True):
    if verbose:
        filename = os.path.basename(filename)
        print(f'uxflint.py:{filename}:{lino}:#{code}:{message}')
    if fail:
        sys.exit(1)


class _Lexer:

    def __init__(self, filename, *, verbose=True):
        self.filename = filename
        self.verbose = verbose
        self.errors = 0
        self.fixes = 0
        with open(filename, 'rt', encoding='utf-8') as file:
            self.text = file.read()


    def error(self, code, message, *, fail=False, fixed=False):
        _error(self.filename, self.lino, code, message, fail=fail,
               verbose=self.verbose)
        self.errors += 1
        if fixed:
            self.fixes += 1


    def clear(self):
        self.pos = 0 # current
        self.lino = 0
        self.custom = None
        self.in_ttype = False
        self.tokens = []


    def tokenize(self):
        self.clear()
        self.scan_header()
        self.maybe_read_comment()
        while not self.at_end():
            self.scan_next()
        self.add_token(_Kind.EOF)
        return self.tokens


    def scan_header(self):
        i = self.text.find('\n')
        if i == -1:
            self.error(100, 'missing UXF file header or empty file',
                       fail=True)
        self.pos = i
        parts = self.text[:i].split(None, 2)
        if len(parts) < 2:
            self.error(110, 'invalid UXF file header', fail=True)
        if parts[0] != 'uxf':
            self.error(120, 'not a UXF file', fail=True)
        try:
            version = float(parts[1])
            if version > uxf.VERSION:
                self.error(131,
                           f'version ({version}) > current ({uxf.VERSION})')
        except ValueError:
            self.error(141, 'failed to read UXF file version number')
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
        if c.isspace(): # ignore insignificant whitespace
            if c == '\n':
                self.lino += 1
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
                _Kind.LIST_BEGIN, _Kind.MAP_BEGIN,
                _Kind.TABLE_BEGIN, _Kind.TTYPE_BEGIN}:
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
            self.add_token(_Kind.REAL if is_real else _Kind.INT,
                           -value)
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
            self.error(221, f'skipped timezone data, used {text[:19]!r}, '
                       f'got {text!r}', fixed=True)
        except ValueError as err:
            self.error(230, f'invalid datetime: {text}: {err}')


    def read_name(self):
        match = self.match_any_of(uxf._BAREWORDS)
        if match in uxf._BOOL_FALSE:
            self.add_token(_Kind.BOOL, False)
            return
        if match in uxf._BOOL_TRUE:
            self.add_token(_Kind.BOOL, True)
            return
        if match in uxf._ANY_VALUE_TYPES:
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
        identifier = self.text[start:self.pos][:uxf.MAX_IDENTIFIER_LEN]
        if identifier:
            return identifier
        text = self.text[start:start + 10]
        self.error(250, f'expected {what}, got {text}…')


    def match_to(self, target, *, error_text):
        if not self.at_end():
            i = self.text.find(target, self.pos)
            if i > -1:
                text = self.text[self.pos:i]
                self.lino += text.count('\n')
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
        self.tokens.append(_Token(kind, value, pos=self.pos,
                                  lino=self.lino))


class _Token(uxf._Token):

    def __init__(self, kind, value=None, *, pos=-1, lino=0):
        super().__init__(kind, value, pos)
        self.lino = lino


    def __str__(self):
        s = super().__str__()
        return f'{self.lino}:{s}'


def _parse(tokens, filename, *, verbose=True):
    parser = _Parser(filename, verbose=verbose)
    data, comment = parser.parse(tokens)
    return data, comment, parser.ttypes, parser.errors, parser.fixes


class _Parser:

    def __init__(self, filename, *, verbose=True):
        self.filename = filename
        self.verbose = verbose
        self.errors = 0
        self.fixes = 0


    def error(self, code, message, *, fail=False, fixed=False):
        _error(self.filename, self.lino, code, message, fail=fail,
               verbose=self.verbose)
        self.errors += 1
        if fixed:
            self.fixes += 1


    def clear(self):
        self.stack = []
        self.ttypes = {}
        self.lino_for_ttype = {}
        self.used_ttypes = set()
        self.pos = -1
        self.lino = 0


    def parse(self, tokens):
        self.clear()
        if not tokens:
            return
        self.tokens = tokens
        data = None
        comment = self._parse_file_comment()
        self._parse_ttypes()
        for i, token in enumerate(self.tokens):
            self.lino = token.lino
            kind = token.kind
            collection_start = self._is_collection_start(kind)
            if data is None and not collection_start:
                self.error(270,
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
                self.error(280, f'unexpected token, got {token}')
        self._check_ttypes()
        return data, comment



    def _check_ttypes(self):
        defined = set(self.ttypes.keys())
        unused = defined - self.used_ttypes
        if unused:
            self._report_ttypes(unused, 'unused')
        undefined = self.used_ttypes - defined
        if undefined:
            self._report_ttypes(undefined, 'undefined')


    def _report_ttypes(self, ttypes, what):
        diff = sorted(ttypes)
        if len(diff) == 1:
            self.error(290, f'{what} type: {diff[0]!r}')
        else:
            diff = ', '.join(repr(t) for t in diff)
            self.error(300, f'{what} types: {diff}')


    def _handle_comment(self, i, token):
        parent = self.stack[-1]
        prev_token = self.tokens[i - 1]
        if not self._is_collection_start(prev_token.kind):
            self.error(310, 'comments may only be put at the beginning '
                       f'of a map, list, or table, not after {prev_token}')
        parent.comment = token.value


    def _handle_identifier(self, i, token):
        parent = self.stack[-1]
        if (self.tokens[i - 1].kind is _Kind.TYPE and
            (self.tokens[i - 2].kind is _Kind.MAP_BEGIN or
                (self.tokens[i - 2].kind is _Kind.COMMENT and
                 self.tokens[i - 3].kind is _Kind.MAP_BEGIN))):
            vtype = self.ttypes.get(token.value)
            if vtype is None:
                self.error(320, f'undefined map value table type, {token}')
            else:
                parent.vtype = vtype.name
                self.used_ttypes.add(vtype.name)
        elif self.tokens[i - 1].kind is _Kind.LIST_BEGIN or (
                self.tokens[i - 1].kind is _Kind.COMMENT and
                self.tokens[i - 2].kind is _Kind.LIST_BEGIN):
            vtype = self.ttypes.get(token.value)
            if vtype is None:
                self.error(330, f'undefined list table type, {token}')
            else:
                parent.vtype = vtype.name
                self.used_ttypes.add(vtype.name)
        elif self.tokens[i - 1].kind is _Kind.TABLE_BEGIN or (
                self.tokens[i - 1].kind is _Kind.COMMENT and
                self.tokens[i - 2].kind is _Kind.TABLE_BEGIN):
            ttype = self.ttypes.get(token.value)
            if ttype is None:
                self.error(340, f'undefined table ttype, {token}',
                           fail=True) # A table with not ttype is invalid
            parent.ttype = ttype
            self.used_ttypes.add(ttype.name)
        else: # should never happen
            self.error(350, 'ttype name may only appear at the start of a '
                       f'map (as the value type), list, or table, {token}')


    def _handle_type(self, i, token):
        parent = self.stack[-1]
        if isinstance(parent, uxf.List):
            if parent.vtype is not None:
                self.error(360, 'can only have at most one vtype for a '
                           f'list, got {token}')
            parent.vtype = token.value
        elif isinstance(parent, uxf.Map):
            if parent.ktype is None:
                parent.ktype = token.value
            elif parent.vtype is None:
                parent.vtype = token.value
            else:
                self.error(370, 'can only have at most one ktype and one '
                           f'vtype for a map, got {token}')
        else:
            self.error(380, 'ktypes and vtypes are only allowed at the '
                       f'start of maps and lists, got {token}')


    def _handle_str(self, i, token):
        value = token.value
        vtype, message = self.typecheck(value)
        if value is not None and vtype is not None and vtype in {
                'bool', 'int', 'real', 'date', 'datetime'}:
            new_value = uxf.naturalize(value)
            if new_value != value:
                self.error(395, f'converted str {value!r} to {vtype}',
                           fixed=True)
                value = new_value
            else:
                self.error(400, message)
        self.stack[-1].append(value)


    def _handle_scalar(self, i, token):
        value = token.value
        vtype, message = self.typecheck(value)
        if value is not None and vtype is not None:
            if vtype == 'real' and isinstance(value, int):
                value = float(value)
                self.error(405, 'converted int to real', fixed=True)
            elif vtype == 'int' and isinstance(value, float):
                value = int(value)
                self.error(415, 'converted real to int', fixed=True)
            else:
                self.error(420, message)
        self.stack[-1].append(value)


    def _on_collection_start(self, token):
        kind = token.kind
        if kind is _Kind.MAP_BEGIN:
            value = uxf.Map()
        elif kind is _Kind.LIST_BEGIN:
            value = uxf.List()
        elif kind is _Kind.TABLE_BEGIN:
            value = uxf.Table()
        else:
            self.error(430, f'expected to create map, list, or table, '
                       f'got {token}')
        if self.stack:
            _, message = self.typecheck(value)
            if message is not None:
                self.error(440, message)
            self.stack[-1].append(value) # add the collection to the parent
        self.stack.append(value) # make the collection the current parent


    def _on_collection_end(self, token):
        if not self.stack:
            self.error(450, f'unexpected {token} suggests unmatched map, '
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
            self.lino = token.lino
            if token.kind is _Kind.COMMENT:
                self.tokens = self.tokens[1:]
                return token.value
        return None


    def _parse_ttypes(self):
        ttype = None
        for index, token in enumerate(self.tokens):
            self.lino = token.lino
            if token.kind is _Kind.TTYPE_BEGIN:
                if ttype is not None and ttype.name is not None:
                    self.ttypes[ttype.name] = ttype
                    self.lino_for_ttype[ttype.name] = self.lino
                ttype = uxf.TType(None)
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
                else:
                    self.error(
                        460,
                        f'encountered type without field name: {token}')
            elif token.kind is _Kind.TTYPE_END:
                if ttype is not None and bool(ttype):
                    self.ttypes[ttype.name] = ttype
                    if ttype.name not in self.lino_for_ttype:
                        self.lino_for_ttype[ttype.name] = self.lino
                self.tokens = self.tokens[index + 1:]
            else:
                break # no TTypes at all


    def typecheck(self, value):
        parent = self.stack[-1]
        if isinstance(parent, uxf.Map):
            vtype = parent.ktype if parent._next_is_key else parent.vtype
        elif isinstance(parent, uxf.List):
            vtype = parent.vtype
        else: # must be a Table
            vtype = parent._next_vtype
        if value is not None and vtype is not None:
            if vtype in _BUILT_IN_NAMES:
                if not isinstance(value, _TYPECHECK_CLASSES[vtype]):
                    message = (f'expected {vtype}, got {type(value)} '
                               f'{value}')
                    return vtype, message
            elif vtype not in self.ttypes:
                message = f'expected {vtype}, got {type(value)} {value}'
                return vtype, message
        return None, None


_TYPECHECK_CLASSES = dict(
    collection=(uxf.List, uxf.Map, uxf.Table), bool=bool,
    bytes=(bytes, bytearray), date=datetime.date,
    datetime=datetime.datetime, int=int, list=uxf.List, map=uxf.Map,
    real=float, str=str, table=uxf.Table)
_BUILT_IN_NAMES = tuple(_TYPECHECK_CLASSES.keys())


if __name__ == '__main__':
    main()
