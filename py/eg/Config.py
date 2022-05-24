#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
This shows a practical use case of saving and loading application
configuration data, preserving comments, providing defaults, and validating.
'''

import enum
import os
import sys

try:
    import uxf
except ImportError: # needed for development
    sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
    import uxf


class Config:

    def __init__(self, filename=None):
        '''All the data is held in self._uxo in UXF format. However, the
        class' properties get and set using the appropriate format (e.g.,
        .symbols as a Symbols enum, etc.)'''
        self.filename = filename
        self._prepare_uxo()
        self._set_defaults()
        if self.filename is not None:
            self.load()


    def _prepare_uxo(self):
        initiallyvisible = uxf.tclass(
            INITIALLYVISIBLE, uxf.Field('min', 'int'),
            uxf.Field('max', 'int'))
        decimal = uxf.tclass(DECIMAL)
        roman = uxf.tclass(ROMAN)
        size = uxf.tclass('size', uxf.Field('width', 'int'),
                          uxf.Field('height', 'int'))
        self._uxo = uxf.Uxf({}, custom='Sudoku')
        self._uxo.comment = 'Sudoku Configuration'
        self._uxo.add_tclasses(initiallyvisible, decimal, roman, size)


    def _set_defaults(self):
        general = uxf.List((
            uxf.Table(self._uxo.tclasses[INITIALLYVISIBLE],
                      records=(28, 32), comment='range 9-72'),
            uxf.Table(self._uxo.tclasses[DECIMAL],
                      comment='Decimal or Roman'),
            uxf.Table(self._uxo.tclasses['size'], records=(-1, -1),
                      comment='width and height >= -1')))
        general.vtype = 'table'
        self._uxo.data = uxf.Map(
            fontsize=18, bgcolour1='lightyellow',
            bgcolour2='#FFE7FF', annotationcolour='red',
            confirmedcolour='blue', numbercolour='navy', pagenumber=1,
            gamenumber=1, general=general)
        self._uxo.data.comment = (
            'fontsize range 8-36; colours HTML-style #HHHHHH or names; '
            'don\'t edit pagenumber and gamenumber')


    def load(self, filename=None):
        if filename is not None:
            self.filename = filename
        try:
            uxo = uxf.load(self.filename)
            self._maybe_merge_comment(self._uxo, uxo)
            self._maybe_merge_comment(self._uxo.data, uxo.data)
            for name, value in uxo.data.items():
                if name == GENERAL:
                    self._load_general(value)
                elif name == FONTSIZE:
                    self.fontsize = value
                elif name == BGCOLOUR1:
                    self.bgcolour1 = value
                elif name == BGCOLOUR2:
                    self.bgcolour2 = value
                elif name == ANNOTATIONCOLOUR:
                    self.annotationcolour = value
                elif name == CONFIRMEDCOLOUR:
                    self.confirmedcolour = value
                elif name == NUMBERCOLOUR:
                    self.numbercolour = value
                elif name == PAGENUMBER:
                    self.pagenumber = value
                elif name == GAMENUMBER:
                    self.gamenumber = value
        except (uxf.Error, OSError) as err:
            print(f'Failed to load configuration file: {err}. '
                  'Will try to create a new one on exit.')


    def _load_general(self, value):
        for table in value:
            if table.ttype == INITIALLYVISIBLE:
                record = table.first
                self.mininitiallyvisible = record.min
                self.maxinitiallyvisible = record.max
            elif table.ttype == SIZE:
                record = table.first
                self.width = record.width
                self.height = record.height
            elif table.ttype == DECIMAL:
                self.symbols = Symbols.DECIMAL
            elif table.ttype == ROMAN:
                self.symbols = Symbols.ROMAN
            if table.comment:
                self._maybe_merge_comment(self._table_of(table.ttype),
                                          table)


    def _maybe_merge_comment(self, old, new):
        if new.comment:
            if not old.comment:
                old.comment = new.comment
            elif new.comment not in old.comment.splitlines():
                old.comment += '\n' + new.comment


    def save(self, filename=None):
        if filename is not None:
            self.filename = filename
        self._uxo.dump(self.filename)


    @property
    def symbols(self):
        symbol, _ = self._symbol_and_index()
        if symbol is not None:
            return symbol
        self._uxo.data[GENERAL].append(
            uxf.Table(self._uxo.tclasses[DECIMAL]))
        return Symbols.DECIMAL


    def _symbol_and_index(self):
        self._symbol_for_name = {symbol.name.upper(): symbol
                                 for symbol in Symbols}
        for i in range(len(self._uxo.data[GENERAL])):
            value = self._uxo.data[GENERAL][i]
            ttype = value.ttype.upper()
            symbol = self._symbol_for_name.get(ttype)
            if symbol is not None:
                return symbol, i
        return None, -1


    @symbols.setter
    def symbols(self, value):
        symbol, i = self._symbol_and_index()
        if symbol is not None:
            if symbol is value:
                return # unchanged
        if i == -1:
            i = len(self._uxo.data[GENERAL])
            self._uxo.data[GENERAL].append(None)
        ttype = value.name.capitalize()
        self._uxo.data[GENERAL][i] = uxf.Table(self._uxo.tclasses[ttype])


    @property
    def fontsize(self):
        return self._uxo.data[FONTSIZE]


    @fontsize.setter
    def fontsize(self, value):
        if isinstance(value, int) and 8 <= value <= 36:
            self._uxo.data[FONTSIZE] = value


    @property
    def width(self):
        return self._table_of(SIZE).first.width


    @width.setter
    def width(self, value):
        if isinstance(value, int) and value >= -1:
            table = self._table_of(SIZE)
            table[0] = (value, table[0].height)


    def _table_of(self, what):
        for i, table in enumerate(self._uxo.data[GENERAL]):
            if table.ttype == what:
                return self._uxo.data[GENERAL][i]


    @property
    def height(self):
        return self._table_of(SIZE).first.height


    @height.setter
    def height(self, value):
        if isinstance(value, int) and value >= -1:
            table = self._table_of(SIZE)
            table[0] = (table[0].width, value)


    @property
    def mininitiallyvisible(self):
        return self._table_of(INITIALLYVISIBLE).first.min


    @mininitiallyvisible.setter
    def mininitiallyvisible(self, value):
        if isinstance(value, int) and 9 <= value <= 72:
            table = self._table_of(INITIALLYVISIBLE)
            table[0] = (value, table[0].max)


    @property
    def maxinitiallyvisible(self):
        return self._table_of(INITIALLYVISIBLE).first.max


    @maxinitiallyvisible.setter
    def maxinitiallyvisible(self, value):
        if isinstance(value, int) and 9 <= value <= 72:
            table = self._table_of(INITIALLYVISIBLE)
            table[0] = (table[0].min, value)


    @property
    def bgcolour1(self):
        return self._uxo.data[BGCOLOUR1]


    @bgcolour1.setter
    def bgcolour1(self, value):
        self._uxo.data[BGCOLOUR1] = value


    @property
    def bgcolour2(self):
        return self._uxo.data[BGCOLOUR2]


    @bgcolour2.setter
    def bgcolour2(self, value):
        self._uxo.data[BGCOLOUR2] = value


    @property
    def annotationcolour(self):
        return self._uxo.data[ANNOTATIONCOLOUR]


    @annotationcolour.setter
    def annotationcolour(self, value):
        self._uxo.data[ANNOTATIONCOLOUR] = value


    @property
    def confirmedcolour(self):
        return self._uxo.data[CONFIRMEDCOLOUR]


    @confirmedcolour.setter
    def confirmedcolour(self, value):
        self._uxo.data[CONFIRMEDCOLOUR] = value


    @property
    def numbercolour(self):
        return self._uxo.data[NUMBERCOLOUR]


    @numbercolour.setter
    def numbercolour(self, value):
        self._uxo.data[NUMBERCOLOUR] = value


    @property
    def pagenumber(self):
        return self._uxo.data[PAGENUMBER]


    @pagenumber.setter
    def pagenumber(self, value):
        if isinstance(value, int):
            self._uxo.data[PAGENUMBER] = value


    @property
    def gamenumber(self):
        return self._uxo.data[GAMENUMBER]


    @gamenumber.setter
    def gamenumber(self, value):
        if isinstance(value, int):
            self._uxo.data[GAMENUMBER] = value


class Symbols(enum.IntEnum):
    DECIMAL = 1
    ROMAN = 2


INITIALLYVISIBLE = 'initiallyvisible'
DECIMAL = 'Decimal'
ROMAN = 'Roman'
GENERAL = 'general'
FONTSIZE = 'fontsize'
SIZE = 'size'
BGCOLOUR1 = 'bgcolour1'
BGCOLOUR2 = 'bgcolour2'
ANNOTATIONCOLOUR = 'annotationcolour'
CONFIRMEDCOLOUR = 'confirmedcolour'
NUMBERCOLOUR = 'numbercolour'
PAGENUMBER = 'pagenumber'
GAMENUMBER = 'gamenumber'
