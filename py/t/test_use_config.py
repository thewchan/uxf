#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
This test is to show a practical use case of saving and loading application
config data.

See ../../testdata/use_config1.conf
'''

import os
import random
import shutil
import sys
import tempfile

try:
    PATH = os.path.abspath(os.path.dirname(__file__))
    old = '/home/mark/bin/sudoku.pyw'
    new = os.path.join(tempfile.gettempdir(), 't/sudoku.py')
    if os.path.isfile(old) and random.choice((0, 1)):
        os.makedirs(os.path.dirname(new), exist_ok=True)
        shutil.copyfile(old, new)
        sys.path.append(os.path.abspath(os.path.dirname(new)))
        from sudoku import Config, Symbols
        SUDOKU = True
    else:
        sys.path.append(os.path.abspath(os.path.join(PATH, '../eg/')))
        from Config import Config, Symbols
        SUDOKU = False
    os.chdir(os.path.join(PATH, '../../testdata')) # move to test data
finally:
    pass


def main():
    regression = False
    if len(sys.argv) > 1 and sys.argv[1] in {'-r', '--regression'}:
        regression = True
    total = ok = 0

    if not regression:
        print('using sudoku.Config' if SUDOKU else 'using eg/Config')

    total += 1
    config = Config('use_config1.conf')
    ok += 1
    if not regression:
        print(config._uxo.dumps())

    total += 1
    if config.width == 540:
        ok += 1
    elif not regression:
        print('fail #1')

    total += 1
    config.width = 99
    if config.width == 99:
        ok += 1
    elif not regression:
        print('fail #2')

    total += 1
    config.symbols = Symbols.ROMAN
    config.fontsize = 19
    config.bgcolour2 = 'magenta'
    if (config.symbols is Symbols.ROMAN and config.fontsize == 19 and
            config.bgcolour2 == 'magenta'):
        ok += 1
    elif not regression:
        print('fail #3')

    # TODO
    # - dumps config to uxt
    # - loads from uxt & use eq() to compare: should be ==
    # - create a new default config & use eq() to compare: should be !=
    # - change all the config values back
    # - compare with default & use eq(): should be ==

    print(f'total={total} ok={ok}')


if __name__ == '__main__':
    main()
