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
        initiallyvisible = uxf.TClass('initiallyvisible',
                                      (uxf.Field('min', 'int'),
                                       uxf.Field('max', 'int')))
        decimal = uxf.TClass('Decimal')
        roman = uxf.TClass('Roman')
        size = uxf.TClass('size', (uxf.Field('width', 'int'),
                                   uxf.Field('height', 'int')))
        self.uxo = uxf.Uxf({})
        self.uxo.add_tclass(initiallyvisible)
        self.uxo.add_tclass(decimal)
        self.uxo.add_tclass(roman)
        self.uxo.add_tclass(size)
        general = uxf.List((
            uxf.Table(initiallyvisible, records=(28, 32)),
            uxf.Table(decimal), uxf.Table(size, records=(-1, -1))))
        general.vtype = 'table'
        self.uxo.data = dict(
            general=general, fontsize=18, bgcolour1='lightyellow',
            bgcolour2='#FFE7FF', annotationcolour='red',
            confirmedcolour='blue', numbercolour='navy', pagenumber=1,
            gamenumber=1)
        if self.filename is not None:
            self.load()


    def load(self, filename=None):
        if filename is not None:
            self.filename = filename
        try:
            uxo = uxf.load(self.filename)
            for name, value in uxo.data.items():
                if name == 'general':
                    for table in value:
                        if table.ttype == 'initiallyvisible':
                            record = table.first
                            self.mininitiallyvisible = record.min
                            self.maxinitiallyvisible = record.max
                        elif table.ttype == 'size':
                            record = table.first
                            self.width = record.width
                            self.height = record.ight
                        elif table.ttype == 'Decimal':
                            self.symbols = Symbols.DECIMAL
                        elif table.ttype == 'Roman':
                            self.symbols = Symbols.ROMAN
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
        i = self._size_index()
        return self.uxo.data['general'][i].first.width


    @width.setter
    def width(self, value):
        if isinstance(value, int) and value >= -1:
            i = self._size_index()
            table = self.uxo.data['general'][i]
            table[0] = (value, table[0][1])


    def _size_index(self):
        for i, value in enumerate(self.uxo.data['general']):
            if value.ttype == 'size':
                return i


    @property
    def height(self):
        i = self._size_index()
        return self.uxo.data['general'][i].first.height


    @height.setter
    def height(self, value):
        if isinstance(value, int) and value >= -1:
            i = self._size_index()
            table = self.uxo.data['general'][i]
            table[0] = (table[0][0], value)


    @property
    def mininitiallyvisible(self):
        return self.uxo.data['mininitiallyvisible']


    @mininitiallyvisible.setter
    def mininitiallyvisible(self, value):
        if isinstance(value, int) and 9 <= value <= 72:
            self.uxo.data['mininitiallyvisible'] = value

    @property
    def maxinitiallyvisible(self):
        return self.uxo.data['maxinitiallyvisible']


    @maxinitiallyvisible.setter
    def maxinitiallyvisible(self, value):
        if isinstance(value, int) and 9 <= value <= 72:
            self.uxo.data['maxinitiallyvisible'] = value


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
