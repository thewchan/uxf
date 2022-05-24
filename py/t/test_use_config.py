#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
This test is to show a practical use case of saving and loading application
config data.

See ../../testdata/use_config1.conf
'''

import enum
import os
import sys

try:
    PATH = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(os.path.join(PATH, '../')))
    import uxf
    os.chdir(os.path.join(PATH, '../../testdata')) # move to test data
finally:
    pass


def main():
    regression = False
    if len(sys.argv) > 1 and sys.argv[1] in {'-r', '--regression'}:
        regression = True
    total = ok = 0

    total += 1
    config = Config('use_config1.conf')
    print(config.uxo.dumps())

    print(f'total={total} ok={ok}')


class Symbols(enum.IntEnum):
    DECIMAL = 1
    ROMAN = 2


class Config:

    def __init__(self, filename=None):
        '''All the data is held in self.uxo in UXF format. However, the
        class' properties get and set using the appropriate format (e.g.,
        .symbols as a Symbols enum)'''
        self.filename = filename
        tclasses = self._prepare_uxo()
        self._set_defaults(tclasses)
        if self.filename is not None:
            self.load()


    def _prepare_uxo(self):
        initiallyvisible = uxf.tclass(
            'initiallyvisible', uxf.Field('min', 'int'),
            uxf.Field('max', 'int'))
        decimal = uxf.tclass('Decimal')
        roman = uxf.tclass('Roman')
        size = uxf.tclass('size', uxf.Field('width', 'int'),
                          uxf.Field('height', 'int'))
        self.uxo = uxf.Uxf({}, custom='Sudoku')
        self.uxo.comment = 'Sudoku Configuration'
        self.uxo.add_tclass(initiallyvisible)
        self.uxo.add_tclass(decimal)
        self.uxo.add_tclass(roman)
        self.uxo.add_tclass(size)
        return initiallyvisible, decimal, roman, size


    def _set_defaults(self, tclasses):
        initiallyvisible, decimal, roman, size = tclasses
        general = uxf.List((
            uxf.Table(initiallyvisible, records=(28, 32),
                      comment='range 9-72'),
            uxf.Table(decimal, comment='Decimal or Roman'),
            uxf.Table(size, records=(-1, -1),
                      comment='width and height >= -1')))
        general.vtype = 'table'
        self.uxo.data = uxf.Map(
            fontsize=18, bgcolour1='lightyellow',
            bgcolour2='#FFE7FF', annotationcolour='red',
            confirmedcolour='blue', numbercolour='navy', pagenumber=1,
            gamenumber=1, general=general)
        self.uxo.data.comment = (
            'fontsize range 8-36; colours HTML-style #HHHHHH or names; '
            'don\'t edit pagenumber and gamenumber')


    def load(self, filename=None):
        if filename is not None:
            self.filename = filename
        try:
            uxo = uxf.load(self.filename)
            self._maybe_merge_comment(self.uxo, uxo)
            self._maybe_merge_comment(self.uxo.data, uxo.data)
            for name, value in uxo.data.items():
                if name == 'general':
                    self._load_general(value)
                elif name == 'fontsize':
                    self.fontsize = value
                elif name == 'bgcolour1':
                    self.bgcolour1 = value
                elif name == 'bgcolour2':
                    self.bgcolour2 = value
                elif name == 'annotationcolour':
                    self.annotationcolour = value
                elif name == 'confirmedcolour':
                    self.confirmedcolour = value
                elif name == 'numbercolour':
                    self.numbercolour = value
                elif name == 'pagenumber':
                    self.pagenumber = value
                elif name == 'gamenumber':
                    self.gamenumber = value
        except (uxf.Error, OSError) as err:
            print(f'Failed to load configuration file: {err}. '
                  'Will try to create a new one on exit.')


    def _load_general(self, value):
        for table in value:
            if table.ttype == 'initiallyvisible':
                record = table.first
                self.mininitiallyvisible = record.min
                self.maxinitiallyvisible = record.max
            elif table.ttype == 'size':
                record = table.first
                self.width = record.width
                self.height = record.height
            elif table.ttype == 'Decimal':
                self.symbols = Symbols.DECIMAL
            elif table.ttype == 'Roman':
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
        self.uxo.dump(self.filename)


    @property
    def symbols(self):
        symbol, _ = self._symbol_and_index()
        if symbol is not None:
            return symbol
        self.uxo.data['general'].append(
            uxf.Table(self.uxo.tclasses['Decimal']))
        return Symbols.DECIMAL


    def _symbol_and_index(self):
        self._symbol_for_name = {symbol.name.upper(): symbol
                                 for symbol in Symbols}
        for i in range(len(self.uxo.data['general'])):
            value = self.uxo.data['general'][i]
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
            i = len(self.uxo.data['general'])
            self.uxo.data['general'].append(None)
        ttype = value.name.capitalize()
        self.uxo.data['general'][i] = uxf.Table(self.uxo.tclasses[ttype])


    @property
    def fontsize(self):
        return self.uxo.data['fontsize']


    @fontsize.setter
    def fontsize(self, value):
        if isinstance(value, int) and 8 <= value <= 36:
            self.uxo.data['fontsize'] = value


    @property
    def width(self):
        return self._table_of('size').first.width


    @width.setter
    def width(self, value):
        if isinstance(value, int) and value >= -1:
            table = self._table_of('size')
            table[0] = (value, table[0].height)


    def _table_of(self, what):
        i = self._index_of(what)
        return self.uxo.data['general'][i] if i is not None else None


    def _index_of(self, what):
        for i, value in enumerate(self.uxo.data['general']):
            if value.ttype == what:
                return i


    @property
    def height(self):
        return self._table_of('size').first.height


    @height.setter
    def height(self, value):
        if isinstance(value, int) and value >= -1:
            table = self._table_of('size')
            table[0] = (table[0].width, value)


    @property
    def mininitiallyvisible(self):
        return self._table_of('initiallyvisible').first.min


    @mininitiallyvisible.setter
    def mininitiallyvisible(self, value):
        if isinstance(value, int) and 9 <= value <= 72:
            table = self._table_of('initiallyvisible')
            table[0] = (value, table[0].max)


    @property
    def maxinitiallyvisible(self):
        return self._table_of('initiallyvisible').first.max


    @maxinitiallyvisible.setter
    def maxinitiallyvisible(self, value):
        if isinstance(value, int) and 9 <= value <= 72:
            table = self._table_of('initiallyvisible')
            table[0] = (table[0].min, value)


    @property
    def bgcolour1(self):
        return self.uxo.data['bgcolour1']


    @bgcolour1.setter
    def bgcolour1(self, value):
        self.uxo.data['bgcolour1'] = value


    @property
    def bgcolour2(self):
        return self.uxo.data['bgcolour2']


    @bgcolour2.setter
    def bgcolour2(self, value):
        self.uxo.data['bgcolour2'] = value


    @property
    def annotationcolour(self):
        return self.uxo.data['annotationcolour']


    @annotationcolour.setter
    def annotationcolour(self, value):
        self.uxo.data['annotationcolour'] = value


    @property
    def confirmedcolour(self):
        return self.uxo.data['confirmedcolour']


    @confirmedcolour.setter
    def confirmedcolour(self, value):
        self.uxo.data['confirmedcolour'] = value


    @property
    def numbercolour(self):
        return self.uxo.data['numbercolour']


    @numbercolour.setter
    def numbercolour(self, value):
        self.uxo.data['numbercolour'] = value


    @property
    def pagenumber(self):
        return self.uxo.data['pagenumber']


    @pagenumber.setter
    def pagenumber(self, value):
        if isinstance(value, int):
            self.uxo.data['pagenumber'] = value


    @property
    def gamenumber(self):
        return self.uxo.data['gamenumber']


    @gamenumber.setter
    def gamenumber(self, value):
        if isinstance(value, int):
            self.uxo.data['gamenumber'] = value


if __name__ == '__main__':
    main()
