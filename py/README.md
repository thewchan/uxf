# Python UXF Library

UXF is a plain text human readable optionally typed storage format. UXF may
serve as a convenient alternative to csv, ini, json, sqlite, toml, xml, or
yaml.

For details of the Uniform eXchange Format (UXF) supported by this library,
see the [UXF Overview](../README.md). ([PyPI link to UXF
Overview](https://github.com/mark-summerfield/uxf/blob/main/README.md).)

- [Introduction](#introduction)
- [API](#api)
    - [Reading and Writing UXF Data](#reading-and-writing-uxf-data)
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

A [List](#list-class) is a Python `collections.UserList` subclass with
`.data` (the list)`, .comment` and `.vtype` attributes. Similarly a
[Map](#map-class) is a Python `collections.UserDict` subclass with `.data`
(the dict), `.comment`, `.ktype`, and `.vtype` attributes. The
[Table](#table-class) class has `.records`, `.comment`, and `.tclass`
attributes; with `.tclass` holding a [TClass](#tclass-class) which in turn
holds the table's `ttype` (i.e., its table type name), and the table's field
names and (optional) types. In all cases a type of `None` signifies that any
type valid for the context may be used.

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

The simplest part of the API loads and saves (dumps) UXF data from/to
strings or files.

A UXF object (called a `uxo` in these docs) has a `.data` attribute that is
always a [List](#list-class) or [Map](#map-class) or [Table](#table-class).
The first two have essentially the same APIs as `list` and `dict`. However,
the recommended way to add an item of data is to use `.append()` which all
three collections support. (In the case of a [Map](#map-class), use two
``.append()``s or the conventional `map[key] = value`.)

For reading UXF data it is easiest to iterate, and to do so recursively, if
the data has nested collections. Note that the `visit.py` example provides a
way of doing this using the visitor design pattern.

### Reading and Writing UXF Data

    load(filename_or_filelike): -> uxo
    loads(uxt): -> uxo

The [load()](#load-def) function reads UXF data from a file or file-like
object, and the [loads()](#loads-def) function reads UXF data from a string.
The returned `uxo` is of type [Uxf](#uxf-class).

In the docs we use `uxo` to refer to a [Uxf](#uxf-class) object and `uxt` to
refer to a string containing a UXF file's text.

    dump(filename_or_filelike, data)
    dumps(data) -> uxt

The [dump()](#dump-def) function writes the data to a file or file-like
object, and the [dumps()](#dumps-def) function writes the data into a string
that's then returned. The data can be a [Uxf](#uxfclass) object or a single
`list`, [List](#list-class), `dict`, [Map](#map-class), or
[Table](#table-class).

### Classes

<a name="uxf-class"></a>
#### Uxf

<a name="list-class"></a>
#### List

<a name="map-class"></a>
#### Map

<a name="table-class"></a>
#### Table

<a name="tclass-class"></a>
#### TClass

<a name="field-class"></a>
#### Field

### Functions

<a name="load-def"></a>
#### load()

<a name="loads-def"></a>
#### loads()

<a name="dump-def"></a>
#### dump()

<a name="dumps-def"></a>
#### dumps()

### Constants

### Command Line Usage

The uxf module can be used as an executable. To see the command line help
run:

    python3 -m uxf -h

or

    path/to/uxf.py -h

### Additional Notes
