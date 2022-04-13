#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import argparse
import csv
import datetime
import json
import pathlib

import uxf


def main():
    config = _get_config()
    config.convert(config)


def _get_config():
    parser = argparse.ArgumentParser(usage=USAGE)
    parser.add_argument('-i', '--indent', type=int, default=2,
                        help='default: 2, range 0-8')
    parser.add_argument('-z', '--compress', help='default: don\'t compress')
    parser.add_argument(
        '-f', '--fieldnames', action='store_true',
        help='if present first row is assumed to be field names; default: '
        'first row is values not fieldnames (only applies to csv infiles)')
    parser.add_argument('file', nargs='+',
                        help='infile(s) and outfile as shown above')
    config = parser.parse_args()
    _postprocess_args(parser, config)
    return config


def _postprocess_args(parser, config):
    if not (0 <= config.indent <= 8):
        config.indent = 2 # sanitize rather than complain
    if len(config.file) < 2:
        parser.error('least two filenames are required')
    config.convert = None
    if len(config.file) > 2:
        _postprocess_csv_args(parser, config)
    else:
        _postprocess_other_args(parser, config)
    if config.convert is None:
        parser.error('cannot perform the requested conversion')
    del config.file
    return config


def _postprocess_csv_args(parser, config):
    if not config.file[-1].upper().endswith(DOT_UXF):
        parser.error('multiple infiles may only be converted to .uxf')
    for name in config.file[:-1]:
        if not name.upper().endswith(DOT_CSV):
            parser.error('multiple infiles may only be .csv files')
    config.convert = multi_csv_to_uxf
    config.infiles = config.file[:-1]
    config.outfile = config.file[-1]


def _postprocess_other_args(parser, config):
    config.infiles = [config.file[0]]
    config.outfile = config.file[-1]
    infile = config.infiles[0].upper()
    outfile = config.outfile.upper()
    if infile.endswith(DOT_UXF) and outfile.endswith(DOT_UXF):
        parser.error('connot convert uxf to uxf, instead use: '
                     'python3 -m uxf infile.uxf outfile.uxf')
    if outfile.endswith(DOT_UXF):
        if infile.endswith(DOT_CSV):
            config.convert = csv_to_uxf
        elif infile.endswith(DOT_INI):
            config.convert = ini_to_uxf
        elif infile.endswith((DOT_JSN, DOT_JSON)):
            config.convert = json_to_uxf
        elif infile.endswith(DOT_SQLITE):
            config.convert = sqlite_to_uxf
        elif infile.endswith(DOT_XML):
            config.convert = xml_to_uxf
    elif infile.endswith(DOT_UXF):
        if outfile.endswith(DOT_CSV):
            config.convert = uxf_to_csv
        elif outfile.endswith((DOT_JSN, DOT_JSON)):
            config.convert = uxf_to_json
        elif outfile.endswith(DOT_SQLITE):
            config.convert = uxf_to_sqlite
        elif outfile.endswith(DOT_XML):
            config.convert = uxf_to_xml


def uxf_to_csv(config):
    data, _ = uxf.load(config.infiles[0])
    if isinstance(data, uxf.Table):
        with open(config.outfile, 'w') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(data.fieldnames)
            for row in data:
                writer.writerow(row)
    elif (isinstance(data, (list, uxf.List)) and data and
            isinstance(data[0], (list, uxf.List)) and data[0] and not
            isinstance(data[0][0], (dict, list, uxf.Map, uxf.List,
                                    uxf.Table))):
        with open(config.outfile, 'w') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
            for row in data:
                writer.writerow(row)
    else:
        raise SystemExit('can only convert a UXF containing a single table '
                         'or a single list of lists of scalars to csv')


def csv_to_uxf(config):
    data, filename = _read_csv_to_data(config)
    uxf.dump(config.outfile, data=data, custom=filename,
             one_way_conversion=True)


def _read_csv_to_data(config):
    data = None
    filename = config.infiles[0]
    with open(filename) as file:
        reader = csv.reader(file)
        for row in reader:
            if data is None:
                if config.fieldnames:
                    data = uxf.Table(name=pathlib.Path(filename).stem,
                                     fieldnames=list(row))
                    continue
                else:
                    data = []
            row = [uxf.naturalize(x) for x in row]
            if isinstance(data, uxf.Table):
                data += row
            else:
                data.append(row)
    return data, filename


def multi_csv_to_uxf(config):
    infiles = config.infiles
    data = []
    for infile in infiles:
        config.infiles = [infile]
        datum, _ = _read_csv_to_data(config)
        data.append(datum)
    uxf.dump(config.outfile, data=data, custom=' '.join(infiles),
             one_way_conversion=True)


def uxf_to_json(config):
    data, _ = uxf.load(config.infiles[0])
    with open(config.outfile, 'wt', encoding=UTF8) as file:
        json.dump(data, file, cls=_JsonEncoder, indent=2)


class _JsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return {JSON_DATETIME: obj.isoformat()}
        if isinstance(obj, datetime.date):
            return {JSON_DATE: obj.isoformat()}
        if isinstance(obj, (bytes, bytearray)):
            return {JSON_BYTES: obj.hex().upper()}
        if isinstance(obj, (list, uxf.List)):
            comment = getattr(obj, COMMENT, None)
            if comment is not None:
                return {JSON_LIST: dict(comment=comment, list=list(obj))}
            return list(obj)
        if isinstance(obj, (dict, uxf.Map)):
            comment = getattr(obj, COMMENT, None)
            if comment is not None:
                return {JSON_MAP: dict(comment=comment, map=dict(obj))}
            return dict(obj)
        if isinstance(obj, uxf.NTuple):
            return {JSON_NTUPLE: obj.astuple}
        if isinstance(obj, uxf.Table):
            return {JSON_TABLE: dict(
                comment=obj.comment, name=obj.name,
                fieldnames=obj.fieldnames, records=obj.records)}
        return json.JSONEncoder.default(self, obj)


def json_to_uxf(config):
    filename = config.infiles[0]
    with open(filename, 'rt', encoding=UTF8) as file:
        data = json.load(file, object_hook=_json_naturalize)
    uxf.dump(config.outfile, data=data, custom=filename)


def _json_naturalize(d):
    if JSON_DATETIME in d:
        return uxf.naturalize(d[JSON_DATETIME])
    if JSON_DATE in d:
        return uxf.naturalize(d[JSON_DATE])
    if JSON_BYTES in d:
        return bytes.fromhex(d[JSON_BYTES])
    if JSON_LIST in d:
        x = uxf.List(d[JSON_LIST]['list'])
        x.comment = d[JSON_LIST][COMMENT]
        return x
    if JSON_MAP in d:
        x = uxf.Map(d[JSON_MAP]['map'])
        x.comment = d[JSON_MAP][COMMENT]
        return x
    elif JSON_NTUPLE in d:
        return uxf.NTuple(*d[JSON_NTUPLE])
    elif JSON_TABLE in d:
        return uxf.Table(name=d[JSON_TABLE]['name'],
                         fieldnames=d[JSON_TABLE]['fieldnames'],
                         records=d[JSON_TABLE]['records'],
                         comment=d[JSON_TABLE][COMMENT])
    return d


JSON_DATETIME = 'UXF^datetime'
JSON_DATE = 'UXF^date'
JSON_BYTES = 'UXF^bytes'
JSON_LIST = 'UXF^list'
JSON_MAP = 'UXF^map'
JSON_NTUPLE = 'UXF^ntuple'
JSON_TABLE = 'UXF^table'


def ini_to_uxf(config):
    print('ini_to_uxf', config) # TODO


def uxf_to_sqlite(config):
    print('uxf_to_sqlite', config) # TODO


def sqlite_to_uxf(config):
    print('sqlite_to_uxf', config) # TODO


def uxf_to_xml(config):
    print('uxf_to_xml', config) # TODO


def xml_to_uxf(config):
    print('xml_to_uxf', config) # TODO


DOT_CSV = '.CSV'
DOT_INI = '.INI'
DOT_JSN = '.JSN'
DOT_JSON = '.JSON'
DOT_SQLITE = '.SQLITE'
DOT_UXF = '.UXF'
DOT_XML = '.XML'
COMMENT = 'comment'
UTF8 = 'utf-8'

USAGE = '''
uxfconvert.py <infile.uxf> <outfile.{csv,json,sqlite,xml}>
uxfconvert.py [-z|--compress] [-i|--indent=N] [-f|--fieldnames]
    <infile.{csv,ini,json,sqlite,xml}> <outfile.uxf>
uxfconvert.py [-z|--compress] [-i|--indent=N] [-f|--fieldnames]
    <infile1.csv> [infile2.csv ... infileM.csv] <outfile.uxf>

Converts to/from uxf format.

Not all conversions are possible; not all conversions are lossless: see below.

The primary purpose of this program is to provide a code example
illustrating how to work with the uxf.py module and UXF data.

To produce compact uxf output use options: -z -i0.

If multiple csv files are given as infiles, the outfile will either be a
list of tables (if the fieldnames option is given), or a list of lists of
scalars otherwise.

Converting from uxf to csv can only be done if the uxf contains a single
table or a single list of lists of scalars.

Converting from uxf to json and back (i.e., using uxfconvert.py's own json
format) should work with perfect fidelity.

Converting sqlite to uxf only converts the sql tables and is unlikely to
roundtrip.

Converting from uxf to xml and back (i.e., using uxfconvert.py's own xml
format) should work with perfect fidelity.

Support for uxf to uxf conversions is provided by the uxf.py module, e.g.,
  python3 -m uxf infile.uxf outfile.uxf
with the same indent and compress options.'''


if __name__ == '__main__':
    main()
