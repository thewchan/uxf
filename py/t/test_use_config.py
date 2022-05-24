#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
This test is to show a practical use case of saving and loading application
config data.

See ../../testdata/use_config1.conf
'''

import sys
import os


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


class Config:

    def __init__(self, filename=None):
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
        try: # can't `self.uxd = uxf.load(…)` because we want to validate
            uxo = uxf.load(self.filename)
            self.uxo.comment = uxo.comment
            self.uxo.comment = uxo.comment
            self.uxo.data.comment = uxo.data.comment
            self.uxo.data.ktype = uxo.data.ktype
            self.uxo.data.vtype = uxo.data.vtype
            general = uxo.data.get('general')
            if general is not None:
                for value in general:
                    print(type(value), value)
        except OSError as err:
            print(f'Failed to load configuration file: {err}. '
                  'Will try to create a new one on exit.')


#    def save(self, filename=None):
#        if filename is not None:
#            self.filename = filename
#        # It would be far easier to store the map item as
#        # <symbols> <DECIMAL> or <symbols> <ROMAN> but I wanted an enum eg.
#        try:
#            symbol = self._uxd.data['symbols']
#            self._uxd.data['symbols'] = uxf.Table(self._symbol_tclass,
#                                                  records=(symbol.name,))
#            self._uxd.dump(self.filename)
#        finally:
#            self._uxd.data['symbols'] = symbol
#
#
#    def update(self, d):
#        # We store the Symbols as an enum but load/save it as a UType
#        for key, value in d.items():
#            setattr(self, key, value)
#
#
#    def __getitem__(self, name):
#        return self.__dict__['_uxd'].data[name]
#
#
#    def __getattr__(self, name):
#        if name in self.__dict__:
#            return self.__dict__[name]
#        if name in self.__dict__['_uxd'].data:
#            return self.__dict__['_uxd'].data[name]
#        raise AttributeError(f'{self.__class__.__name__!r} object has no '
#                             f'attribute {name!r}')
#
#
#    def __setattr__(self, name, value):
#        if name in self.__dict__:
#            self.__dict__[name] = value
#            return
#        if name not in self._uxd.data:
#            raise AttributeError(f'{self.__class__.__name__!r} object '
#                                 f'has no attribute {name!r}')
#        elif (name in {'maxinitiallyvisible', 'mininitiallyvisible'} and
#                not (isinstance(value, int) and (9 <= value <= 72))):
#            return # ignore bad value
#        elif (name == 'fontsize' and not (isinstance(value, int) and
#              (8 <= value <= 36))):
#            return # ignore bad value
#        elif name == 'symbols':
#            if not isinstance(value, Symbols): # use Symbols value as-is
#                if (not isinstance(value, uxf.Table) or
#                        value.ttype != 'Symbol'):
#                    return # ignore bad value
#                record = value.first
#                if record is None:
#                    return # ignore missing value
#                for symbol in Symbols:
#                    if symbol.name == record.name:
#                        value = symbol
#                        break
#                else:
#                    return # ignore bad value
#        self._uxd.data[name] = value


if __name__ == '__main__':
    main()
