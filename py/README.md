# Python UXF Library

UXF is a plain text human readable optionally typed storage format. UXF may
serve as a convenient alternative to csv, ini, json, sqlite, toml, xml, or
yaml.

For details of the Uniform eXchange Format (UXF) supported by this library,
see the [UXF Overview](../README.md). ([PyPI link to UXF
Overview](https://github.com/mark-summerfield/uxf/blob/main/README.md).)

- [Introduction](#introduction)
- [API](#api)
    - [Classes](#classes)
    - [Functions](#functions)
    - [Constants](#constants)
    - [Command Line Usage](#command-line-usage)

## Introduction

The Python `uxf` library works out of the box with the standard library, and
will use _dateutil_ if available.

- Install: `python3 -m pip install uxf`
- Run: `python3 -m uxf -h` _# this shows the command line help_
- Use: `import uxf` _# see the `uxf.py` module docs for the API_

Most Python types convert losslessly to and from UXF types. In particular:

|**Python Type**     |**UXF type**|
|--------------------|------------|
|`None`              | `null`     |
|`bool`              | `bool`     |
|`int`               | `int`      |
|`float`             | `real`     |
|`datetime.date`     | `date`     |
|`datetime.datetime` | `datetime` |
|`str`               | `str`      |
|`bytes`             | `bytes`    |
|`bytearray`         | `bytes`    |
|`uxf.List`          | `list`     |
|`uxf.Map`           | `map`      |
|`uxf.Table`         | `table    `|

A `uxf.List` is a Python `collections.UserList` subclass with `.data` (the
list)`, .comment` and `.vtype` attributes. Similarly a `uxf.Map` is a Python
`collections.UserDict` subclass with `.data` (the dict), `.comment`,
`.ktype`, and `.vtype` attributes. The `uxf.Table` class has `.records`,
`.comment`, and `.fields` attributes; with `.fields` holding a list of
`uxf.Field` values (which each has a field name and type). In all cases a
type of `None` signifies that any type valid for the context may be used.

For complex numbers you could define a _ttype_ such as: `= Complex Real real
Imag real`. Then you could include single complex values like `(Complex 1.5
7.2)`, or many of them such as `(Complex 1.5 7.2 8.3 -9.4 14.8 0.6)`.

For custom types (e.g., enums; or as an alternative to using a _ttype_ for
complex numbers, or for any other custom type), use `uxf.add_converter()`.
See `test_converters.py` for examples.

Collection types such as `set`, `frozenset`, `tuple`, or `collections.deque`
are automatically converted to a `List` when they are encountered. Of
course, these are one way conversions.

Using `uxf` as an executable (with `python3 -m uxf ...`) provides a means of
doing `.uxf` to `.uxf` conversions (e.g., compress or uncompress, or make
more human readable or more compact).

Installed alongside `uxf.py` is `uxfconvert.py` which might prove useful to
see how to use `uxf`. For example, `uxfconvert.py` can losslessly convert
`.uxf` to `.json` or `.xml` and back. It can also do some simple conversions
to and from `.csv`, to `.ini`, and to and from `.sqlite`, but these are
really to illustrate use of the uxf APIs. And also see the UXF test files in
the `../testdata` folder and the Python examples in the `./eg` folder.

If you just want to create a small standalone `.pyz`, simply copy
`py/uxf.py` as `uxf.py` into your project folder and inlude it in your
`.pyz` file.

## API

### Reading and Writing UXF Data

    load(filename_or_filelike): -> uxo
    loads(uxt): -> uxo

These functions read UXF data from a file, file-like, or string.
The returned `uxo` is of type [Uxf](#uxf-class)
See the function docs for additional options.

In the docs we use uxo to refer to a Uxf object and uxt to refer to a string
containing a UXF file's text.

    dump(filename_or_filelike, data)
    dumps(data) -> uxt

These functions write UXF data to a file, file-like, or string. The data can
be a Uxf object or a single list, List, dict, Map, or Table. dump() writes
the data to the filename\_or\_filelike; dumps() writes the data into a
string that's then returned. See [dump](#dump) and [dumps](#dumps) for full
details.

### Classes

#### Uxf {#uxf-class}

### Functions

### Constants

### Command Line Usage

The uxf module can be used as an executable. To see the command line help
run:

    python3 -m uxf -h

or

    path/to/uxf.py -h

### Additional Notes
