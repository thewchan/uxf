#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

import uxf

# uxfconvert [-z|--compress] [-i|--indent=n]
#	     <infile1.csv [infile2.csv ... infileN.csv]
#	     |infile.{csv,ini,json,uxf,sqlite,toml,xml,yaml}>
#	     [<outfile.{csv,ini,json,uxf,sqlite,toml,xml,yaml}>]
#
# Convert a file (or csv files) to or from UXF format.
#
# These options only apply to UXF output:
# -i|--indent default 2 range 0-8
# -z|--compress default don't compress
#
# To produce minimize UXF output size use -z -i0.
#
# Converting uxf to csv can only be done if the UXF contains a single
# table. Converting csv to uxf produces a uxf containing a list of one
# or more tables.
# Converting sqlite to uxf only converts tables, so like many of the
# possible conversions, this conversion does not round-trip.
#
# uxf to uxf conversions are also supported by the uxf.py module, e.g.,
#   python3 -m uxf infile.uxf outfile.uxf
# with the same indent and compress options.
#
# If an infile or outfile is given with an unrecognized suffix,
# uxfconvert will try to guess.


def main():
    # TODO
    print('uxf', uxf.VERSION, uxf.__version__)


if __name__ == '__main__':
    main()
