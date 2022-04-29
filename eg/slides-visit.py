#!/usr/bin/env python3
# Copyright © 2022 Mark Summerfield. All rights reserved.
# License: GPLv3

'''
This reads slides.uxf and outputs slides/index.html and slides/N.html where
N is a slide number.

This program is just an illustration of the flexibility of the UXF format.
It also shows how even an empty table can be useful (e.g., the nl ttype).
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
        titles.append(write_slide(index, uxf_obj, slide, len(slides)))
    index += 1
    titles.append(write_uxf_source(index))
    index += 1
    titles.append(write_py_source(index))
    write_index(titles)


def write_slide(index, uxf_obj, slide, last):
    with open(f'{OUTDIR}/{index}.html', 'wt', encoding='utf-8') as file:
        file.write('<html><title>')
        title = slide[0]
        doc_title = title[0].content
        file.write(f'{escape(doc_title)}</title><body>\n')
        function = functools.partial(visitor, file=file)
        uxf_obj.visit(function, slide)
        file.write(f'<a href="{index - 1}.html">Prev</a>' if index > 1 else
                   '<a href="index.html">Prev</a>')
        file.write('&nbsp;<a href="index.html">Contents</a>&nbsp;')
        file.write(f'<a href="{index + 1}.html">Next</a>' if index != last
                   else '<font color="gray">Next</font>')
        file.write('</body></html>')
    return doc_title


def visitor(kind, value=None, *, file):
    if kind is uxf.ValueType.TABLE_BEGIN:
        name = value.name
        if name == 'B':
            file.write('<ul><li>')
        elif name in {'h1', 'h2'}:
            file.write(f'<{name}>')
        elif name == 'i':
            file.write('<i>')
        elif name == 'm':
            file.write('<tt>')
        elif name == 'p':
            file.write('<p>')
    elif kind is uxf.ValueType.TABLE_END:
        name = value.name
        if name == 'B':
            file.write('</li></ul>')
        elif name in {'h1', 'h2'}:
            file.write(f'</{name}>')
        elif name == 'i':
            file.write('</i>')
        elif name == 'm':
            file.write('</tt>')
        elif value == 'p':
            file.write('</p>\n')
    elif kind is uxf.ValueType.SCALAR:
        if value is not None:
            file.write(escape(str(value)))
    else:
        print('visitor', kind, str(value)[:100]) # TODO delete


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
    filename = 'slides.py'
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
