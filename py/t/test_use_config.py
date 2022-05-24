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
        self.uxo.data = dict(
            general=[uxf.Table(initiallyvisible, records=(28, 32)),
                     uxf.Table(decimal), uxf.Table(size, records=(-1, -1))],
            fontsize=18, bgcolour1='lightyellow', bgcolour2='#FFE7FF',
            annotationcolour='red', confirmedcolour='blue',
            numbercolour='navy', pagenumber=1, gamenumber=1)
        if self.filename is not None:
            self.load()


    def load(self, filename=None):
        if filename is not None:
            self.filename = filename
        try:
            tclasses = self.uxo.tclasses
            self.uxo = uxf.load(self.filename)
            self.uxo.tclasses.update(tclasses) # make sure they're all there
        except OSError as err:
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


    # TODO add a property getter/setter for every config item, validating &
    # converting types on-demand

#        elif (name in {'maxinitiallyvisible', 'mininitiallyvisible'} and
#                not (isinstance(value, int) and (9 <= value <= 72))):
#            return # ignore bad value
#        elif (name == 'fontsize' and not (isinstance(value, int) and
#              (8 <= value <= 36))):
#            return # ignore bad value


if __name__ == '__main__':
    main()
