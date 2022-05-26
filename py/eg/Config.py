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
        decimal = uxf.tclass(DECIMAL, comment='Or Roman')
        roman = uxf.tclass(ROMAN, comment='Or Decimal')
        size = uxf.tclass('size', uxf.Field('width', 'int'),
                          uxf.Field('height', 'int'))
        numbers = uxf.tclass('numbers', uxf.Field('page', 'int'),
                             uxf.Field('game', 'int'),
                             comment='internal use')
        self._uxo = uxf.Uxf({}, custom='Sudoku')
        self._uxo.comment = 'Sudoku Configuration'
        self._uxo.add_tclasses(initiallyvisible, decimal, roman, size,
                               numbers)


    def _set_defaults(self):
        general = uxf.List((
            uxf.Table(self._uxo.tclasses[INITIALLYVISIBLE],
                      records=(28, 32), comment='range 9-72'),
            uxf.Table(self._uxo.tclasses[DECIMAL],
                      comment='Decimal or Roman'),
            uxf.Table(self._uxo.tclasses['size'], records=(-1, -1),
                      comment='width and height >= -1'),
            uxf.Table(self._uxo.tclasses['numbers'], records=(1, 1),
                      comment='internal use: don\'t edit')), vtype='table')
        colours = uxf.Map(dict(bg1='lightyellow', bg2='#FFE7FF',
                               annotation='red', confirmed='blue',
                               number='navy'), ktype='str', vtype='str',
                          comment='colours HTML-style #HHHHHH or names')
        self._uxo.data = uxf.Map(dict(fontsize=18, general=general,
                                      colours=colours),
                                 comment='fontsize range 8-36')


    def load(self, filename=None):
        if filename is not None:
            self.filename = filename
        try:
            uxo = uxf.load(self.filename)
            self._maybe_merge_comment(self._uxo, uxo)
            self._maybe_merge_comment(self._uxo.data, uxo.data)
            for name, value in uxo.data.items():
                if name == COLOURS:
                    self._load_colours(value)
                elif name == GENERAL:
                    self._load_general(value)
                elif name == FONTSIZE:
                    self.fontsize = value
        except (uxf.Error, OSError) as err:
            print(f'Failed to load configuration file: {err}. '
                  'Will try to create a new one on exit.')


    def _load_colours(self, value):
        for name, colour in value.items():
            if name in COLOURNAMES:
                self[name] = colour


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
            elif table.ttype == NUMBERS:
                record = table.first
                self.pagenumber = record.page
                self.gamenumber = record.game
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
        for i, value in enumerate(self._uxo.data[GENERAL]):
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
            self._table_of(SIZE).first.width = value


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
            self._table_of(SIZE).first.height = value


    @property
    def mininitiallyvisible(self):
        return self._table_of(INITIALLYVISIBLE).first.min


    @mininitiallyvisible.setter
    def mininitiallyvisible(self, value):
        if isinstance(value, int) and 9 <= value <= 72:
            self._table_of(INITIALLYVISIBLE).first.min = value


    @property
    def maxinitiallyvisible(self):
        return self._table_of(INITIALLYVISIBLE).first.max


    @maxinitiallyvisible.setter
    def maxinitiallyvisible(self, value):
        if isinstance(value, int) and 9 <= value <= 72:
            self._table_of(INITIALLYVISIBLE).first.max = value


    @property
    def pagenumber(self):
        return self._table_of(NUMBERS).first.page


    @pagenumber.setter
    def pagenumber(self, value):
        if isinstance(value, int):
            self._table_of(NUMBERS).first.page = value


    @property
    def gamenumber(self):
        return self._table_of(NUMBERS).first.game


    @gamenumber.setter
    def gamenumber(self, value):
        if isinstance(value, int):
            self._table_of(NUMBERS).first.game = value


    @property
    def bgcolour1(self):
        return self._uxo.data[COLOURS][BGCOLOUR1]


    @bgcolour1.setter
    def bgcolour1(self, value):
        if value != '':
            self._uxo.data[COLOURS][BGCOLOUR1] = value


    @property
    def bgcolour2(self):
        return self._uxo.data[COLOURS][BGCOLOUR2]


    @bgcolour2.setter
    def bgcolour2(self, value):
        if value != '':
            self._uxo.data[COLOURS][BGCOLOUR2] = value


    @property
    def annotationcolour(self):
        return self._uxo.data[COLOURS][ANNOTATIONCOLOUR]


    @annotationcolour.setter
    def annotationcolour(self, value):
        if value != '':
            self._uxo.data[COLOURS][ANNOTATIONCOLOUR] = value


    @property
    def confirmedcolour(self):
        return self._uxo.data[COLOURS][CONFIRMEDCOLOUR]


    @confirmedcolour.setter
    def confirmedcolour(self, value):
        if value != '':
            self._uxo.data[COLOURS][CONFIRMEDCOLOUR] = value


    @property
    def numbercolour(self):
        return self._uxo.data[COLOURS][NUMBERCOLOUR]


    @numbercolour.setter
    def numbercolour(self, value):
        if value != '':
            self._uxo.data[COLOURS][NUMBERCOLOUR] = value


    def __getitem__(self, name):
        basename = name.replace('colour', '')
        if basename in COLOURNAMES:
            return self._uxo.data[COLOURS][basename]
        raise Error(f'{self.__class__.__name__} ignored invalid colour '
                    f'attribute name {name!r}')


    def __setitem__(self, name, value):
        basename = name.replace('colour', '')
        if basename in COLOURNAMES:
            if value != '':
                self._uxo.data[COLOURS][basename] = value
        else:
            raise Error(f'{self.__class__.__name__} can\'t set invalid '
                        f'colour attribute name {name!r}')


class Symbols(enum.IntEnum):
    DECIMAL = 1
    ROMAN = 2


class Error(Exception):
    pass


INITIALLYVISIBLE = 'initiallyvisible'
DECIMAL = 'Decimal'
ROMAN = 'Roman'
GENERAL = 'general'
FONTSIZE = 'fontsize'
SIZE = 'size'
NUMBERS = 'numbers'
COLOURS = 'colours'
BGCOLOUR1 = 'bg1'
BGCOLOUR2 = 'bg2'
ANNOTATIONCOLOUR = 'annotation'
CONFIRMEDCOLOUR = 'confirmed'
NUMBERCOLOUR = 'number'
COLOURNAMES = {BGCOLOUR1, BGCOLOUR2, ANNOTATIONCOLOUR, CONFIRMEDCOLOUR,
               NUMBERCOLOUR}
