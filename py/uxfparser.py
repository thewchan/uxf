#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

# If this turns out to be faster/more memory efficient than the current
# uxf._Parser, drop it in as a replacement; otherwise merge it into uxf.py
# as an additional API.

'''
- UxfParser an incremental parser that calls 'event' methods similar
  to HtmlParser.

  class UxfParser:

    def __init__(raw, on_error=uxf.on_error, populate_uxo=True):
        # raw is bytes, bytearray, a file opened in 'rb' mode, a str
        # filename (which will be opened in 'rb' mode), or a memory map.
        # With populate_uxo=True this reads byte-by-byte incrementally
        # populating a Uxf object.
        self.populate = populate_uxo
        if self.populate:
            self.uxo = uxf.Uxf()
        ...

    def on_custom(self, custom:str):
        if self.populate:
            self.uxo.custom = custom

    def on_import(self, filename:str):
        if self.populate:
            ... do the import and merge imported ttypes into self.uxo.ttypes

  You can override any on_* method, e.g., to trace. Or if you don't want to
  create a Uxf object but just want the data set populate_uxo=False and
  implement all the methods you care about to do what you want.

- Uxf.loadi(raw, on_error=on_error) and loadi(raw, on_error=on_error)
  These use UxfParser under the hood.
'''
