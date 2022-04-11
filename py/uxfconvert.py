#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import argparse
import enum

import uxf


def main():
    config = get_config()
    print(config)


def get_config():
    parser = argparse.ArgumentParser(usage=USAGE)
    parser.add_argument('-i', '--indent', type=int, default=2,
                        help='default 2, range 0-8')
    parser.add_argument('-z', '--compress', help='default don\'t compress')
    parser.add_argument('-f', '--fieldnames',
                        help='default first row is values not fieldnames '
                        '(only applies to csv infiles)')
    parser.add_argument('file', nargs='+',
                        help='infile(s) and outfile as shown above')
    config = parser.parse_args()
    if not (0 <= config.indent <= 8):
        config.indent = 2 # sanitize rather than complain
    if len(config.file) < 2:
        parser.error('least two filenames are required')
    config.mode = None
    if len(config.file) > 2:
        if not config.file[-1].upper().endswith('.UXF'):
            parser.error('multiple infiles may only be converted to .uxf')
        for name in config.file[:-1]:
            if not name.upper().endswith('.CSV'):
                parser.error('multiple infiles may only be .csv files')
        config.mode = Mode.MULTI_CSV_TO_UXF
        config.infiles = config.file[:-1]
        config.outfile = config.file[-1]
    else:
        config.infiles = [config.file[0]]
        config.outfile = config.file[-1]
        infile = config.infiles[0].upper()
        outfile = config.outfile.upper()
        if infile.endswith('.UXF') and outfile.endswith('.UXF'):
            parser.error('connot convert uxf to uxf, instead use: '
                         'python3 -m uxf infile.uxf outfile.uxf')
        if outfile.endswith('.UXF'):
            if infile.endswith('.CSV'):
                config.mode = Mode.CSV_TO_UXF
            elif infile.endswith('.INI'):
                config.mode = Mode.INI_TO_UXF
            elif infile.endswith(('.JSN', '.JSON')):
                config.mode = Mode.JSON_TO_UXF
            elif infile.endswith('.SQLITE'):
                config.mode = Mode.SQLITE_TO_UXF
            elif infile.endswith('.XML'):
                config.mode = Mode.XML_TO_UXF
        elif infile.endswith('.UXF'):
            if outfile.endswith('.CSV'):
                config.mode = Mode.UXF_TO_CSV
            elif outfile.endswith('.INI'):
                config.mode = Mode.UXF_TO_INI
            elif outfile.endswith(('.JSN', '.JSON')):
                config.mode = Mode.UXF_TO_JSON
            elif outfile.endswith('.SQLITE'):
                config.mode = Mode.UXF_TO_SQLITE
            elif outfile.endswith('.XML'):
                config.mode = Mode.UXF_TO_XML
    if config.mode is None:
        parser.error('cannot perform the requested conversion')
    del config.file
    return config


@enum.unique
class Mode(enum.Enum):
    UXF_TO_CSV = enum.auto()
    UXF_TO_INI = enum.auto()
    UXF_TO_JSON = enum.auto()
    UXF_TO_SQLITE = enum.auto()
    UXF_TO_XML = enum.auto()
    CSV_TO_UXF = enum.auto()
    MULTI_CSV_TO_UXF = enum.auto()
    INI_TO_UXF = enum.auto()
    JSON_TO_UXF = enum.auto()
    SQLITE_TO_UXF = enum.auto()
    XML_TO_UXF = enum.auto()


USAGE = '''
uxfconvert.py <infile.uxf> <outfile.{csv,ini,json,sqlite,xml}>
uxfconvert.py [-z|--compress] [-i|--indent=N] [-f|--fieldnames]
    <infile.{csv,ini,json,sqlite,xml}> <outfile.uxf>
uxfconvert.py [-z|--compress] [-i|--indent=N] [-f|--fieldnames]
    <infile1.csv> [infile2.csv ... infileM.csv] <outfile.uxf>

Converts to/from uxf format.
Not all conversions are possible; not all conversions are lossless.

The primary purpose of this program is to provide a code example
illustrating how to work with the uxf.py module and UXF data.

To produce the smallest uxf output use options: -z -i0.

If multiple csv files are given as infiles, the outfile will be a uxf
containing a list of tables. If the fieldnames option is given the first
line of each csv file will be assumed to be field names rather than values.

Converting from uxf to csv can only be done if the uxf contains a single
table.

Converting sqlite to uxf only converts tables, so like many of the
possible conversions, this conversion does not round-trip.

Converting xml to uxf only works for the xml that is output by
uxfconvert.py when converting from uxf to xml.

uxf to uxf conversions are also supported by the uxf.py module, e.g.,
  python3 -m uxf infile.uxf outfile.uxf
with the same indent and compress options.'''


if __name__ == '__main__':
    main()
