#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import uxf



def main():
    # TODO use argparse?
    # TODO make sure the suffixes work
    print(USAGE)


USAGE = '''\
uxfconvert.py <infile.uxf> <outfile.{csv,ini,json,sqlite,xml}>
uxfconvert.py [-z|--compress] [-i|--indent=N] [-f|--fieldnames]
    <infile.{csv,ini,json,sqlite,xml}> <outfile.uxf>
uxfconvert.py [-z|--compress] [-i|--indent=N] [-f|--fieldnames]
    <infile1.csv> [infile2.csv ... infileM.csv] <outfile.uxf>

Options:
  -i | --indent     default 2, range 0-8
  -z | --compress   default don't compress
  -f | --fieldnames default no fieldnames (only applies to csv infiles)

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
