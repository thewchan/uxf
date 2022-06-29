#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import filecmp
import functools
import os
import sys
import tempfile

try:
    PATH = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(os.path.join(PATH, '../')))
    import uxf
    sys.path.append(os.path.abspath(os.path.join(PATH, '../eg/')))
    import compare
    os.chdir(os.path.join(PATH, '../../testdata')) # move to test data
finally:
    pass


def main():
    regression = False
    if len(sys.argv) > 1 and sys.argv[1] in {'-r', '--regression'}:
        regression = True
    total = ok = 0

    on_error = functools.partial(uxf.on_error, verbose=False)

    # Two files with the equivalent UXF content; but different actual
    # content
    filename1 = 't63.uxf'
    filename2 = os.path.join(tempfile.gettempdir(), '63.uxf')
    uxo = uxf.load(filename1, drop_unused=True, replace_imports=True)
    uxo.dump(filename2, on_error=on_error)

    total += 1
    if not filecmp.cmp(filename1, filename2, shallow=False):
        ok += 1
    elif not regression:
        print('1 filecmp.cmp() • FAIL files compared unexpectedly the same')

    total += 1
    if not compare.compare(filename1, filename2, on_error=on_error):
        ok += 1
    elif not regression:
        print('2 compare() • FAIL files compared unexpectedly equal')

    total += 1
    if compare.compare(filename1, filename2, equivalent=True,
                       on_error=on_error):
        ok += 1
    elif not regression:
        print(
            '3 compare() • FAIL files compared unexpectedly nonequivalent')

    # Two files with the equivalent UXF content; but different actual
    # content (whitespace only)
    filename1 = 't13.uxf'
    filename2 = 'expected/t13.uxf'

    total += 1
    if not filecmp.cmp(filename1, filename2, shallow=False):
        ok += 1
    elif not regression:
        print('4 filecmp.cmp() • FAIL files compared unexpectedly the same')

    total += 1
    if compare.compare(filename1, filename2, on_error=on_error):
        ok += 1
    elif not regression:
        print('5 compare() • FAIL files compared unexpectedly unequal')

    total += 1
    if compare.compare(filename1, filename2, equivalent=True,
                       on_error=on_error):
        ok += 1
    elif not regression:
        print(
            '6 compare() • FAIL files compared unexpectedly nonequivalent')

    print(f'total={total} ok={ok}')


if __name__ == '__main__':
    main()
