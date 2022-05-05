#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
This reads slides.uxf and outputs slides/index.html and slides/N.html where
N is a slide number.

This program is just an illustration of the flexibility of the UXF format.
It also shows how to use the visit example module's visit() function and the
use of empty tables (e.g., (nl)).

slides2.py is slightly shorter because it manually traverses UXF data; it is
also more flexible and robust for this particular slides format.
'''

import base64
import functools
import os
import shutil
import sys
from xml.sax.saxutils import escape


def import_module(module_name, location):
    import importlib
    path = os.path.abspath('.')
    os.chdir(os.path.dirname(__file__))
    spec = importlib.util.spec_from_file_location(module_name, location)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    os.chdir(path)
    return module


try:
    import uxf
    import visit
except ImportError: # needed for development
    uxf = import_module('uxf', '../py/uxf.py')
    visit = import_module('visit', '../py/visit.py')


def main():
    infile, outdir = get_args()
    shutil.rmtree(outdir, ignore_errors=True)
    os.mkdir(outdir)
    uxo = uxf.load(infile)
    titles = []
    slides = uxo.data
    for index, slide in enumerate(slides, 1):
        titles.append(write_slide(outdir, index, slide, len(slides)))
    index += 1
    titles.append(write_uxf_source(outdir, index, infile))
    index += 1
    titles.append(write_py_source(outdir, index))
    write_index(outdir, titles)


def get_args():
    if len(sys.argv) < 3 or sys.argv[1] in {'-h', '--help'}:
        raise SystemExit('usage: slides1.py <infile.sld> <outdir>]')
    infile = sys.argv[1]
    outdir = sys.argv[2]
    return infile, outdir


def write_slide(outdir, index, slide, last):
    with open(f'{outdir}/{index}.html', 'wt', encoding='utf-8') as file:
        file.write('<html><title>')
        title = slide[0]
        doc_title = title[0].content
        file.write(f'{escape(doc_title)}</title><body>\n')
        function = functools.partial(visitor, state=State(file))
        visit.visit(function, slide)
        file.write(f'<a href="{index - 1}.html">Prev</a>' if index > 1 else
                   '<a href="index.html">Prev</a>')
        file.write('&nbsp;<a href="index.html">Contents</a>&nbsp;')
        file.write(f'<a href="{index + 1}.html">Next</a>' if index != last
                   else '<font color="gray">Next</font>')
        file.write('</body></html>')
    return escape(doc_title)


class State:

    def __init__(self, file):
        self.file = file
        self.in_image = False
        self.link_title = None # not in url


def visitor(kind, value=None, *, state):
    Kind = visit.ValueType
    if kind is Kind.TABLE_BEGIN:
        name = value.name
        if name == 'B':
            state.file.write('<ul><li>')
        elif name in {'h1', 'h2', 'p', 'pre'}:
            state.file.write(f'<{name}>')
        elif name == 'i':
            state.file.write(' <i>')
        elif name == 'img':
            state.in_image = True
        elif name == 'm':
            state.file.write(' <tt>')
        elif name == 'nl':
            pass
        elif name == 'url':
            state.link_title = ''
    elif kind is Kind.TABLE_END:
        name = value.name
        if name == 'B':
            state.file.write('</li></ul>')
        elif name in {'h1', 'h2', 'p', 'pre'}:
            state.file.write(f'</{name}>\n')
        elif name == 'i':
            state.file.write('</i> ')
        elif name == 'img':
            state.in_image = False
        elif name == 'm':
            state.file.write('</tt> ')
        elif name == 'nl':
            state.file.write('<br />\n')
        elif name == 'url':
            state.link_title = '' # want link title
    elif kind is Kind.BYTES:
        if state.in_image:
            data = base64.urlsafe_b64encode(value).decode('ascii')
            state.file.write(f'<img src="data:image/png;base64,{data}" />')
    elif kind is Kind.STR:
        if state.link_title == '': # empty means want link title
            state.link_title = escape(value)
        elif bool(state.link_title): # nonempty means have link title
            state.file.write(f' <a href="{value}">{state.link_title}</a> ')
            state.link_title = None # None means not in url
        else:
            state.file.write(escape(value))
    elif kind in {Kind.BOOL, Kind.INT, Kind.REAL, Kind.DATE,
                  Kind.DATE_TIME}:
        state.file.write(str(value))
    elif kind in {Kind.LIST_BEGIN, Kind.LIST_END, Kind.ROW_BEGIN,
                  Kind.ROW_END}:
        pass
    else:
        print(f'Unexpected value {value!r} of type {kind}')


def write_uxf_source(outdir, index, infile):
    with open(infile, 'rt', encoding='utf-8') as file:
        text = file.read()
    title = escape(os.path.basename(infile))
    with open(f'{outdir}/{index}.html', 'wt', encoding='utf-8') as file:
        file.write(f'<html><title>{title}</title><body>\n<h1>{title}</h1>')
        file.write(f'<pre>\n{escape(text)}\n</pre>')
    return title


def write_py_source(outdir, index):
    with open(__file__, 'rt', encoding='utf-8') as file:
        text = file.read()
    title = escape(os.path.basename(__file__))
    with open(f'{outdir}/{index}.html', 'wt', encoding='utf-8') as file:
        file.write(f'<html><title>{title}</title><body>\n<h1>{title}</h1>')
        file.write(f'<pre>\n{escape(text)}\n</pre>')
    return title


def write_index(outdir, titles):
    with open(f'{outdir}/index.html', 'wt', encoding='utf-8') as file:
        title = escape(titles[0])
        file.write(
            f'<html><title>{title}</title><body>\n<h1>{title}</h1><ol>')
        for i, title in enumerate(titles, 1):
            file.write(f'<li><a href="{i}.html">{title}</a></li>\n')
        file.write('</ol></body></html>')


if __name__ == '__main__':
    main()
