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


def main():
    if len(sys.argv) < 2 or sys.argv[1] in {'-h', '--help'}:
        raise SystemExit('''usage: uxflint.py <infile> [outfile]
If an outfile is specified (or - for stdout) the infile is saved to it \
with the following fixes:
- the format is standardized (just like using uxf.py infile outfile)
- unused ttypes are removed
''') # TODO update for each fix that's applied
    infile = sys.argv[1]
    outfile = sys.argv[2] if len(sys.argv) > 2 else None
    if outfile is not None and (os.path.abspath(infile) ==
                                os.path.abspath(outfile)):
        raise SystemExit(f'won\'t overwite {infile}')
    uxf.AutoConvertSequences = True
    lexer = Lexer(infile)
    tokens = lexer.tokenize()
    data, comment, ttypes = parse(tokens, filename=infile)
    if outfile is not None:
        uxo = uxf.Uxf(data, custom=lexer.custom, ttypes=ttypes,
                      comment=comment)
        if outfile == '-':
            print(uxo.dumps())
        else:
            uxo.dump(outfile)


def say(filename, lino, code, message, *, fail=False):
    filename = os.path.basename(filename)
    print(f'uxflint.py:{filename}:{lino}:#{code}:{message}')
    if fail:
        sys.exit(1)


class Lexer:

    def __init__(self, filename):
        self.filename = filename
        with open(filename, 'rt', encoding='utf-8') as file:
            self.text = file.read()


    def say(self, code, message, *, fail=False):
        say(self.filename, self.lino, code, message, fail=fail)


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
        self.add_token(uxf._Kind.EOF)
        return self.tokens


    def scan_header(self):
        i = self.text.find('\n')
        if i == -1:
            say(100, 'missing UXF file header or empty file', fail=True)
        self.pos = i
        parts = self.text[:i].split(None, 2)
        if len(parts) < 2:
            say(110, 'invalid UXF file header', fail=True)
        if parts[0] != 'uxf':
            say(120, 'not a UXF file', fail=True)
        try:
            version = float(parts[1])
            if version > uxf.VERSION:
                say(131, f'version ({version}) > current ({uxf.VERSION})')
        except ValueError:
            say(141, 'failed to read UXF file version number')
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
                self.add_token(uxf._Kind.COMMENT, unescape(value))
            else:
                self.say(150, 'invalid comment syntax: expected \'<\', '
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
                self.add_token(uxf._Kind.TABLE_BEGIN)
        elif c == ')':
            self.add_token(uxf._Kind.TABLE_END)
        elif c == '[':
            self.check_in_ttype()
            self.add_token(uxf._Kind.LIST_BEGIN)
        elif c == '=':
            self.add_token(uxf._Kind.TTYPE_BEGIN)
            self.in_ttype = True
        elif c == ']':
            self.add_token(uxf._Kind.LIST_END)
        elif c == '{':
            self.check_in_ttype()
            self.add_token(uxf._Kind.MAP_BEGIN)
        elif c == '}':
            self.in_ttype = False
            self.add_token(uxf._Kind.MAP_END)
        elif c == '?':
            self.add_token(uxf._Kind.NULL)
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
            self.say(160, f'invalid character encountered: {c!r}')


    def check_in_ttype(self):
        if self.in_ttype:
            self.in_ttype = False
            self.add_token(uxf._Kind.TTYPE_END)


    def read_comment(self):
        if self.tokens and self.tokens[-1].kind in {
                uxf._Kind.LIST_BEGIN, uxf._Kind.MAP_BEGIN,
                uxf._Kind.TABLE_BEGIN, uxf._Kind.TTYPE_BEGIN}:
            if self.peek() != '<':
                self.say(170, 'a str must follow the # comment '
                         f'introducer, got {self.peek()!r}')
            self.pos += 1 # skip the leading <
            value = self.match_to('>',
                                  error_text='unterminated comment string')
            self.add_token(uxf._Kind.COMMENT, unescape(value))
        else:
            self.say(180, 'comments may only occur at the start of '
                     'TTypes, Maps, Lists, and Tables')


    def read_string(self):
        value = self.match_to('>', error_text='unterminated string')
        self.add_token(uxf._Kind.STR, unescape(value))


    def read_bytes(self):
        value = self.match_to(':)', error_text='unterminated bytes')
        try:
            self.add_token(uxf._Kind.BYTES, bytes.fromhex(value))
        except ValueError as err:
            self.say(190, f'expected bytes, got {value!r}: {err}')


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
            self.add_token(uxf._Kind.REAL if is_real else uxf._Kind.INT,
                           -value)
        except ValueError as err:
            self.say(200, f'invalid number: {text}: {err}')


    def read_positive_number_or_date(self, c):
        start = self.pos - 1
        is_real, is_datetime, hyphens = self.read_number_or_date_chars(c)
        self.pos -= 1 # wind back to terminating non-numeric non-date char
        text = self.text[start:self.pos]
        convert, token = self.get_converter_and_token(is_real, is_datetime,
                                                      hyphens, text)
        try:
            value = convert(text)
            if token is uxf._Kind.DATE and isoparse is not None:
                value = value.date()
            self.add_token(token, value)
        except ValueError as err:
            if is_datetime and len(text) > 19:
                self.reread_datetime(text, convert)
            else:
                self.say(210, f'invalid number or date/time: {text}: {err}')


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
            return convert, uxf._Kind.DATE
        if is_real:
            return float, uxf._Kind.REAL
        return int, uxf._Kind.INT


    def read_datetime(self, text):
        if isoparse is None:
            convert = datetime.datetime.fromisoformat
            if text.endswith('Z'):
                text = text[:-1] # Py std lib can't handle UTC 'Z'
        else:
            convert = isoparse
        convert = (datetime.datetime.fromisoformat if isoparse is None
                   else isoparse)
        return convert, uxf._Kind.DATE_TIME


    def reread_datetime(self, text, convert):
        try:
            value = convert(text[:19])
            self.add_token(uxf._Kind.DATE_TIME, value)
            self.say(221, f'skipped timezone data, used {text[:19]!r}, '
                     f'got {text!r}')
        except ValueError as err:
            self.say(230, f'invalid datetime: {text}: {err}')


    def read_name(self):
        match = self.match_any_of(uxf._BAREWORDS)
        if match in uxf._BOOL_FALSE:
            self.add_token(uxf._Kind.BOOL, False)
            return
        if match in uxf._BOOL_TRUE:
            self.add_token(uxf._Kind.BOOL, True)
            return
        if match in uxf._ANY_VALUE_TYPES:
            self.add_token(uxf._Kind.TYPE, match)
            return
        start = self.pos - 1
        if self.text[start] == '_' or self.text[start].isalpha():
            identifier = self. match_identifier(start, 'identifier')
            self.add_token(uxf._Kind.IDENTIFIER, identifier)
        else:
            i = self.text.find('\n', self.pos)
            text = self.text[self.pos - 1:i if i > -1 else self.pos + 8]
            self.say(240, f'expected const or identifier, got {text!r}')


    def read_field_vtype(self):
        self.skip_ws()
        identifier = self.match_identifier(self.pos, 'field vtype')
        self.add_token(uxf._Kind.TYPE, identifier)


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
        self.say(250, f'expected {what}, got {text}…')


    def match_to(self, target, *, error_text):
        if not self.at_end():
            i = self.text.find(target, self.pos)
            if i > -1:
                text = self.text[self.pos:i]
                self.lino += text.count('\n')
                self.pos = i + len(target) # skip past target
                return text
        self.say(260, error_text)


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
        self.tokens.append(Token(kind, value, pos=self.pos, lino=self.lino))


class Token(uxf._Token):

    def __init__(self, kind, value=None, *, pos=-1, lino=0):
        super().__init__(kind, value, pos)
        self.lino = lino


    def __str__(self):
        s = super().__str__()
        return f'{self.lino}:{s}'


def parse(tokens, filename):
    parser = Parser(filename)
    data, comment = parser.parse(tokens)
    ttypes = parser.ttypes
    return data, comment, ttypes


class Parser:

    def __init__(self, filename):
        self.filename = filename


    def say(self, code, message, *, fail=False):
        say(self.filename, self.lino, code, message, fail=fail)


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
                self.say(400,
                         f'expected a map, list, or table, got {token}')
            if collection_start:
                self._on_collection_start(token)
                if data is None:
                    data = self.stack[0]
            elif self._is_collection_end(kind):
                self._on_collection_end(token)
            elif kind is uxf._Kind.COMMENT:
                self._handle_comment(i, token)
            elif kind is uxf._Kind.IDENTIFIER:
                self._handle_identifier(i, token)
            elif kind is uxf._Kind.TYPE:
                self._handle_type(i, token)
            elif kind is uxf._Kind.STR:
                self.stack[-1].append(token.value)
            elif kind.is_scalar:
                self.stack[-1].append(token.value)
            elif kind is uxf._Kind.EOF:
                break
            else:
                self.say(410, f'unexpected token, got {token}')
        self._check_unused_ttypes()
        return data, comment


    def _handle_comment(self, i, token):
        parent = self.stack[-1]
        prev_token = self.tokens[i - 1]
        if not self._is_collection_start(prev_token.kind):
            self.say(420, 'comments may only be put at the beginning '
                     f'of a map, list, or table, not after {prev_token}')
        parent.comment = token.value


    def _handle_identifier(self, i, token):
        parent = self.stack[-1]
        if not isinstance(parent, uxf.Table):
            self.say(430, 'ttype name may only appear at the start of a '
                     f'table, {token}')
        if self.tokens[i - 1].kind is uxf._Kind.TABLE_BEGIN or (
                self.tokens[i - 1].kind is uxf._Kind.COMMENT and
                self.tokens[i - 2].kind is uxf._Kind.TABLE_BEGIN):
            ttype = self.ttypes.get(token.value)
            if ttype is None:
                self.say(440, f'undefined table ttype, {token}')
            parent.ttype = ttype
            self.used_ttypes.add(ttype.name)
        else: # should never happen
            self.say(450, 'ttype name may only appear at the start of a '
                     f'table, {token}')


    def _handle_type(self, i, token):
        parent = self.stack[-1]
        if isinstance(parent, uxf.List):
            if parent.vtype is not None:
                self.say(460, 'can only have at most one vtype for a '
                         f'list, got {token}')
            parent.vtype = token.value
        elif isinstance(parent, uxf.Map):
            if parent.ktype is None:
                parent.ktype = token.value
            elif parent.vtype is None:
                parent.vtype = token.value
            else:
                self.say(470, 'can only have at most one ktype and one '
                         f'vtype for a map, got {token}')
        else:
            self.say(480, 'ktypes and vtypes are only allowed at the '
                     f'start of maps and lists, got {token}')


    def _on_collection_start(self, token):
        kind = token.kind
        if kind is uxf._Kind.MAP_BEGIN:
            value = uxf.Map()
        elif kind is uxf._Kind.LIST_BEGIN:
            value = uxf.List()
        elif kind is uxf._Kind.TABLE_BEGIN:
            value = uxf.Table()
        else:
            self.say(490,
                     f'expected to create map, list, or table, got {token}')
        if self.stack:
            self.stack[-1].append(value) # add the collection to the parent
        self.stack.append(value) # make the collection the current parent


    def _on_collection_end(self, token):
        if not self.stack:
            self.say(500, f'unexpected {token} suggests unmatched map, '
                     'list, or table start/end pair')
        self.stack.pop()


    def _is_collection_start(self, kind):
        return kind in {uxf._Kind.MAP_BEGIN, uxf._Kind.LIST_BEGIN,
                        uxf._Kind.TABLE_BEGIN}


    def _is_collection_end(self, kind):
        return kind in {uxf._Kind.MAP_END, uxf._Kind.LIST_END,
                        uxf._Kind.TABLE_END}


    def _parse_file_comment(self):
        if self.tokens:
            token = self.tokens[0]
            self.lino = token.lino
            if token.kind is uxf._Kind.COMMENT:
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
            self.lino = token.lino
            if token.kind is uxf._Kind.TTYPE_BEGIN:
                if ttype is not None and ttype.name is not None:
                    self.ttypes[ttype.name] = ttype
                    self.lino_for_ttype[ttype.name] = self.lino
                ttype = uxf.TType(None)
            elif token.kind is uxf._Kind.COMMENT:
                ttype.comment = token.value
            elif token.kind is uxf._Kind.IDENTIFIER:
                if ttype.name is None:
                    ttype.name = token.value
                else:
                    ttype.append(token.value)
            elif token.kind is uxf._Kind.TYPE:
                if len(ttype) > 0:
                    vtype = token.value
                    ttype.set_vtype(-1, vtype)
                    if vtype not in uxf.TYPENAMES:
                        used.add(vtype)
                else:
                    self.say(
                        510,
                        f'encountered type without field name: {token}')
            elif token.kind is uxf._Kind.TTYPE_END:
                if ttype is not None and bool(ttype):
                    self.ttypes[ttype.name] = ttype
                    if ttype.name not in self.lino_for_ttype:
                        self.lino_for_ttype[ttype.name] = self.lino
                self.tokens = self.tokens[index + 1:]
            else:
                break # no TTypes at all
        return used


    def _check_used_ttypes(self, used):
        if self.ttypes: # Check that all ttypes referred to are defined
            defined = set(self.ttypes.keys())
            diff = used - defined
            if diff:
                diff = sorted(diff)
                if len(diff) == 1:
                    self.say(520, f'ttype uses undefined type: {diff[0]!r}')
                else:
                    diff = ', '.join(repr(t) for t in diff)
                    self.say(530, f'ttype uses undefined types: {diff}')


    def _check_unused_ttypes(self):
        diff = set(self.ttypes.keys()) - self.used_ttypes
        if diff:
            for name in diff:
                del self.ttypes[name]
            diff = sorted(diff)
            if len(diff) == 1:
                self.lino = self.lino_for_ttype[diff[0]]
                self.say(540, f'ttype {diff[0]!r} is unused')
            else:
                linos = [self.lino_for_ttype[ttype] for ttype in diff]
                pairs = sorted(zip(linos, diff))
                linos = [str(p[0]) for p in pairs]
                self.lino = ','.join(linos)
                diff = ', '.join([p[1] for p in pairs])
                self.say(550, f'ttypes {diff} are unused')


if __name__ == '__main__':
    main()
