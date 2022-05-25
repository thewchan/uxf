#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
This test is to show a practical use case of saving and loading application
config data.

See ../../testdata/use_config1.conf
'''

import os
import sys

try:
    PATH = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(os.path.join(PATH, '../')))
    sys.path.append(os.path.abspath(os.path.join(PATH, '../eg/')))
    import Config
    os.chdir(os.path.join(PATH, '../../testdata')) # move to test data
finally:
    pass


def main():
    regression = False
    if len(sys.argv) > 1 and sys.argv[1] in {'-r', '--regression'}:
        regression = True
    total = ok = 0

    total += 1
    config = Config.Config('use_config1.conf')
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
    config.symbols = Config.Symbols.ROMAN
    config.fontsize = 19
    config.bgcolour2 = 'magenta'
    if (config.symbols is Config.Symbols.ROMAN and config.fontsize == 19 and
            config.bgcolour2 == 'magenta'):
        ok += 1
    elif not regression:
        print('fail #3')

    # TODO
    # - load from the file;
    # - change various properties (plus some invalid changes)
    # - check the valid changes have been applied
    # - ?

    print(f'total={total} ok={ok}')


if __name__ == '__main__':
    main()
