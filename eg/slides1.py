#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
This reads slides.uxf and outputs slides/index.html and slides/N.html where
N is a slide number.

This program is just an illustration of the flexibility of the UXF format.
It also shows how to use the uxf.visit() function and the use of empty
tables (e.g., (nl)).

See slides2.py for a solution that involves manually traversing the UXF
data.
'''

import base64
import functools
import shutil
import sys
from xml.sax.saxutils import escape

INFILE = 'slides.uxf'
OUTDIR = 'slides'

try:
    import uxf
except ImportError: # needed for development
    import os
    import importlib
    os.chdir(os.path.dirname(__file__))
    module_name = 'uxf'
    spec = importlib.util.spec_from_file_location(module_name,
                                                  '../py/uxf.py')
    uxf = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = uxf
    spec.loader.exec_module(uxf)


def main():
    shutil.rmtree(OUTDIR, ignore_errors=True)
    os.mkdir(OUTDIR)
    uxf_obj = uxf.load(INFILE)
    titles = []
    slides = uxf_obj.data
    for index, slide in enumerate(slides, 1):
        titles.append(write_slide(index, slide, len(slides)))
    index += 1
    titles.append(write_uxf_source(index))
    index += 1
    titles.append(write_py_source(index))
    write_index(titles)


def write_slide(index, slide, last):
    with open(f'{OUTDIR}/{index}.html', 'wt', encoding='utf-8') as file:
        file.write('<html><title>')
        title = slide[0]
        doc_title = title[0].content
        file.write(f'{escape(doc_title)}</title><body>\n')
        function = functools.partial(visitor, file=file, state=State())
        uxf.visit(function, slide)
        file.write(f'<a href="{index - 1}.html">Prev</a>' if index > 1 else
                   '<a href="index.html">Prev</a>')
        file.write('&nbsp;<a href="index.html">Contents</a>&nbsp;')
        file.write(f'<a href="{index + 1}.html">Next</a>' if index != last
                   else '<font color="gray">Next</font>')
        file.write('</body></html>')
    return doc_title


class State:

    def __init__(self):
        self.in_image = False
        self.link_title = None # not in url


def visitor(kind, value=None, *, file, state):
    if kind in {uxf.ValueType.LIST_BEGIN, uxf.ValueType.LIST_END,
                uxf.ValueType.ROW_BEGIN, uxf.ValueType.ROW_END}:
        pass
    elif kind is uxf.ValueType.TABLE_BEGIN:
        name = value.name
        if name == 'B':
            file.write('<ul><li>')
        elif name in {'h1', 'h2', 'p', 'pre'}:
            file.write(f'<{name}>')
        elif name == 'i':
            file.write(' <i>')
        elif name == 'img':
            state.in_image = True
        elif name == 'm':
            file.write(' <tt>')
        elif name == 'nl':
            pass
        elif name == 'url':
            state.link_title = ''
    elif kind is uxf.ValueType.TABLE_END:
        name = value.name
        if name == 'B':
            file.write('</li></ul>')
        elif name in {'h1', 'h2', 'p', 'pre'}:
            file.write(f'</{name}>\n')
        elif name == 'i':
            file.write('</i> ')
        elif name == 'img':
            state.in_image = False
        elif name == 'm':
            file.write('</tt> ')
        elif name == 'nl':
            file.write('<br />\n')
        elif name == 'url':
            state.link_title = '' # want link title
    elif kind is uxf.ValueType.BYTES:
        if state.in_image:
            data = base64.urlsafe_b64encode(value).decode('ascii')
            file.write(f'<img src="data:image/png;base64,{data}" />')
    elif kind is uxf.ValueType.STR:
        if state.link_title == '': # empty means want link title
            state.link_title = escape(value)
        elif bool(state.link_title): # nonempty means have link title
            file.write(f' <a href="{value}">{state.link_title}</a> ')
            state.link_title = None # None means not in url
        else:
            file.write(escape(value))
    elif kind in {uxf.ValueType.BOOL, uxf.ValueType.INT, uxf.ValueType.REAL,
                  uxf.ValueType.DATE, uxf.ValueType.DATE_TIME}:
        file.write(str(value))


def write_uxf_source(index):
    filename = 'slides.uxf'
    with open(filename, 'rt', encoding='utf-8') as file:
        text = file.read()
    title = escape(filename)
    with open(f'{OUTDIR}/{index}.html', 'wt', encoding='utf-8') as file:
        file.write(f'<html><title>{title}</title><body>\n<h1>{title}</h1>')
        file.write(f'<pre>\n{escape(text)}\n</pre>')
    return filename


def write_py_source(index):
    filename = 'slides1.py'
    with open(filename, 'rt', encoding='utf-8') as file:
        text = file.read()
    title = escape(filename)
    with open(f'{OUTDIR}/{index}.html', 'wt', encoding='utf-8') as file:
        file.write(f'<html><title>{title}</title><body>\n<h1>{title}</h1>')
        file.write(f'<pre>\n{escape(text)}\n</pre>')
    return filename


def write_index(titles):
    with open(f'{OUTDIR}/index.html', 'wt', encoding='utf-8') as file:
        title = escape(titles[0])
        file.write(
            f'<html><title>{title}</title><body>\n<h1>{title}</h1><ol>')
        for i, title in enumerate(titles, 1):
            title = escape(title)
            file.write(f'<li><a href="{i}.html">{title}</a></li>\n')
        file.write('</ol></body></html>')


if __name__ == '__main__':
    main()
