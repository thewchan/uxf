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
    parts = ['<html><title>']
    doc_title = title = html_for_block(slide[0])
    while len(doc_title) > 1:
        doc_title = doc_title[1:-1]
    parts += doc_title
    parts.append('</title><body>')
    parts += title
    for block in slide[1:]:
        parts += html_for_block(block)
    parts.append(f'<a href="{index - 1}.html">Prev</a>' if index > 1 else
                 '<a href="index.html">Prev</a>')
    parts.append('&nbsp;<a href="index.html">Contents</a>&nbsp;')
    parts.append(f'<a href="{index + 1}.html">Next</a>' if index != last
                 else '<font color="gray">Next</font>')
    parts.append('</body></html>')
    with open(f'{OUTDIR}/{index}.html', 'wt', encoding='utf-8') as file:
        file.write('\n'.join(parts))
    return doc_title[0]


def html_for_block(block):
    if isinstance(block, str):
        return [escape(block)]
    if isinstance(block, uxf.List):
        parts = []
        for value in block:
            parts += html_for_block(value)
        return parts
    # ∴ must be a Table
    parts = []
    end = None
    if block.name == 'B':
        parts.append('<ul><li>')
        end = '</li></ul>'
    elif block.name in {'h1', 'h2'}:
        parts.append(f'<{block.name}>')
        end = f'</{block.name}>'
    elif block.name == 'i':
        parts.append('<i>')
        end = '</i>'
    elif block.name == 'img':
        record = block[0]
        data = base64.urlsafe_b64encode(record.image).decode('ascii')
        parts.append(f'<img src="data:image/png;base64,{data}" />')
        parts += html_for_block(record.content)
        if end is not None:
            parts.append(end)
        return parts
    elif block.name == 'm':
        parts.append('<tt>')
        end = '</tt>'
    elif block.name == 'nl':
        parts.append('<br />')
    elif block.name == 'p':
        parts.append('<p>')
        end = '</p>'
    elif block.name == 'pre':
        parts.append('<pre>')
        end = '</pre>'
    elif block.name == 'url':
        record = block[0]
        parts.append(f'<a href="{record.link}">')
        parts += html_for_block(record.content)
        end = '</a>'
        if end is not None:
            parts.append(end)
        return parts
    for record in block:
        parts += html_for_block(record.content)
    if end is not None:
        parts.append(end)
    return parts


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
