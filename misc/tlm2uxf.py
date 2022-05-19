#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
uxf 1.0 TLM 1.1
#<Track lists are represented by maps with name keys.
Their values may be Tracks or sublists.
The special __History__ key is invalid as a list name and is used to hold
the recent track history; other special keys are possible.
>
=Track filename:str seconds:real
{
  <ABBA> (Track
      </home/mark/music/ABBA/CD1/01-People_Need_Love.ogg> 165.773
      </home/mark/music/ABBA/CD1/02-He_Is_Your_Brother.ogg> 198.440
  )
  <Amelie> (Track
      </home/mark/music/Amelie/01-J_y_suis_jamais_all.ogg> 94.467
      </home/mark/music/Amelie/02-Les_jours_tristes_instrumental.ogg> 183.467
      </home/mark/music/Amelie/03-La_valse_d_Am_lie.ogg> 135.907
  )
  <Classical> {
    <Bach> (Track
        </home/mark/music/J.S._Bach/Orchestral_Suites_Nos.1-4/01-Suite_No.1_in_C_BWV1066_-I_Ouvert_re.ogg> 361.973
        </home/mark/music/J.S._Bach/Orchestral_Suites_Nos.1-4/02-Suite_No.1_in_C_BWV1066_-II_Courante.ogg> 124.533
    )
    <Bartok> (Track
        </home/mark/music/Bela_Bartok/CD1/01-Piano_Concerto_No._1-I._Allegro_moderato.ogg> 550.000
        </home/mark/music/Bela_Bartok/CD1/02-Piano_Concerto_No._1-II._Andante_-.ogg> 497.493
    )
  }
  <__History__> [
    <Classical/Prokofiev/Piano Concerto No. 3 in C major Op. 26 I. Andante Allegro>
    <Classical/Prokofiev/Piano Concerto No. 2 in G minor Op. 16 IV. Allegro tempestoso>
    <Blondie/Denis>
  ]
}
''' # noqa: E501


import gzip
import os
import sys
from xml.sax.saxutils import escape


def main():
    if len(sys.argv) == 1 or sys.argv[1] in {'-h', '--help'}:
        raise SystemExit('usage: tlm2uxf.py <filename.tlm>')
    infile = sys.argv[1]
    outfile = infile.replace('.tlm', '.uxf')
    #print('wrote', outfile)


if __name__ == '__main__':
    main()
