# Python UXF Library

UXF is a plain text human readable optionally typed storage format. UXF may
serve as a convenient alternative to csv, ini, json, sqlite, toml, xml, or
yaml.

For details of the Uniform eXchange Format (UXF) supported by this library,
see the [UXF Overview](../README.md). ([PyPI link to UXF
Overview](https://github.com/mark-summerfield/uxf/blob/main/README.md).)

- [Introduction](#introduction)
- [Python UXF Types](#python-uxf-types)
- [API](#api)
    - [Reading and Writing UXF Data](#reading-and-writing-uxf-data)
    - [API Notes](#api-notes)
    - [Classes](#classes)
    - [Functions](#functions)
    - [Constants](#constants)
    - [Command Line Usage](#command-line-usage)

## Introduction

The Python `uxf` library works out of the box with the standard library and
one dependency,
[editabletuple](https://github.com/mark-summerfield/editabletuple). And it
will use [dateutil](https://pypi.org/project/python-dateutil/) if it's
available.

- Install: `python3 -m pip install uxf` (or download the wheel `.whl`
  files and do `python -m pip install uxf....whl
  editabletuple...whl` where ... varies)
- Run: `python3 -m uxf -h` _# this shows the command line help_
- Use: `import uxf` _# see the `uxf.py` module docs for the API_

Using `uxf` as an executable (e.g., `python3 -m uxf ...`) provides a means
of doing `.uxf` to `.uxf` conversions (e.g., compress or uncompress or to
use the standard pretty print format). The executable can also be used for
linting and for replacing imports to ensure that UXF files are stand-alone.

Installed alongside `uxf.py` are `uxflint.py`, and `uxfconvert.py` which
might prove useful to see how to use `uxf`. For example, `uxfconvert.py` can
losslessly convert `.uxf` to `.json` or `.xml` and back. It can also do some
simple conversions to and from `.csv`, to `.ini`, and to and from `.sqlite`,
but these are really to illustrate use of the uxf APIs. And also see the UXF
test files in the `../testdata` folder, the Python examples in the `eg`
folder, and the Python tests in the `t` folder.

If you just want to create a small standalone `.pyz`, you could simply copy
`py/uxf.py` as `uxf.py` into your project folder and include it in your
`.pyz` file.

## Python UXF Types

Most Python types convert losslessly to and from UXF types. In particular:

|**Python Type**     |**UXF type**|
|--------------------|------------|
|`None`              | `null`     |
|`bool`              | `bool`     |
|`bytes`             | `bytes`    |
|`bytearray`         | `bytes`    |
|`datetime.date`     | `date`     |
|`datetime.datetime` | `datetime` |
|`int`               | `int`      |
|`float`             | `real`     |
|`str`               | `str`      |
|`uxf.List`          | `list`     |
|`uxf.Map`           | `map`      |
|`uxf.Table`         | `table    `|

A [List](#list-class) is a Python `collections.UserList` subclass with
`.data` (the list)`, .comment` and `.vtype` attributes. A `.vtype` holds a
`str` representing the name of the corresponding UXF type (e.g., `int`,
`real`, etc.) or a `ttype` (the name of a custom table type; see
[TClass](#tclass-class)). If a `.vtype` is `None` it means that _any_ UXF
type may be stored.

Similarly a [Map](#map-class) is a Python `collections.UserDict` subclass
with `.data` (the dict), `.comment`, `.ktype`, and `.vtype` attributes. The
`.ktype` is a `str` like the `.vtype` except that it may only be `None`
(accept any valid _ktype_) or one of `bytes`, `date`, `datetime`, `int`, or
`str`. The `.vtype` works just the same as for [List](#list-class)s.

The [Table](#table-class) class has `.records`, `.comment`, and `.tclass`
attributes; with `.tclass` holding a [TClass](#tclass-class) which in turn
holds the table's `ttype` (i.e., its table type name), and the table's field
names and (optional) types. In all cases a type of `None` signifies that any
type valid for the context may be used.

Non-UXF types can be represented using _ttypes_. For example, for points you
could define a _ttype_ such as: `=point x:real y:real`. Then you could
include single points like `(point 1.5 7.2)`, or many of them such as
`(point 1.5 7.2 8.3 -9.4 14.8 0.6)`.

Collection types such as `set`, `frozenset`, `tuple`, or `collections.deque`
are automatically converted to a [List](#list-class) when they are
encountered. Of course, these are one way conversions.

## API

The simplest part of the API loads and saves (dumps) UXF data from/to
strings or files.

### Reading and Writing UXF Data

    load(filename_or_filelike): -> uxo
    loads(uxt): -> uxo

The [load()](#load-def) function reads UXF data from a file or file-like
object, and the [loads()](#loads-def) function reads UXF data from a string.
The returned `uxo` is of type [Uxf](#uxf-class).

    dump(filename_or_filelike, data)
    dumps(data) -> uxt

The [dump()](#dump-def) function writes the data to a file or file-like
object, and the [dumps()](#dumps-def) function writes the data into a string
that's then returned (here called `uxt` to indicate UXF text). The data can
be a [Uxf](#uxfclass) object or a single `list`, [List](#list-class),
`dict`, [Map](#map-class), or [Table](#table-class).

If the data contains values of types that aren't supported by UXF, they
could either be transformed in advance (e.g., to a custom table type, a
_ttype_).

See also the examples in the `eg` folder and the tests in the `t` folder.

### API Notes

A [UXF](#uxf-class) object (called a `uxo` in these docs) has a `.data`
attribute that is always a [List](#list-class) or [Map](#map-class) or
[Table](#table-class). The first two have essentially the same APIs as
`list` and `dict` respectively. The [Table](#table-class) API is a little
similar to a `list`. Individual records can be accessed using `[]`, but to
work with records or fields the API provides `get_record()`, `set_record()`,
`get_field()`, `set_field()`, amongst others. For small tables, records can
be accessed with the `first`, `second`, `third`, or `fourth` properties. The
best way to append new records is to use the [Table](#table-class)'s
`append()` method.

The `uxf` module distinguishes between a _ttype_ (the name of a user-defined
table) and a [TClass](#tclass-class) (the Python class which represents a
user-defined table). A [TClass](#tclass-class) has `.ttype` and `.fields`
attributes.

For reading UXF data it is easiest to iterate, and to do so recursively, if
the data has nested collections. Note that the `visit.py` example provides a
way of doing this using the visitor design pattern. The `uxfconvert.py`
example shows alternative approaches to manual iteration.

Note that for imports, if the filename is relative it is searched for in the
same folder as the importing UXF file, and if not found there, each of the
paths in `UXF_PATH` is tried in turn (if any).

Note that the `__version__` is the module version (i.e., the version of this
implementation), while the `VERSION` is the maximum UXF version that this
module can read (and the UXF version that it writes).

### Classes

The classes are documented in importance order. Here are alphabetically
ordered links:
[Error](#error-class),
[Field](#field-class),
[List](#list-class),
[Map](#map-class),
[TClass](#tclass-class),
[Table](#table-class),
[Uxf](#uxf-class).

<a name="uxf-class"></a>
#### Uxf

A `Uxf` object represents UXF data.

The easiest way to obtain a `Uxf` object is to use one of the module-level
functions, [load()](#load-def) or [loads()](#loads-def). Of course, you can
also create ``Uxf``s programatically (as shown in many of the examples and
tests).

The `.data` attribute holds a [List](#list-class), [Map](#map-class), or
[Table](#table-class). Since these classes can nest, a `Uxf` can represent
any arbitrary data structure.

The `.custom` attribute is an opional `str` used for customizing the file
format.

The `.tclasses` attribute is a possibly empty `dict` where each key is a
`ttype` (i.e., the `.tclass.ttype` which is a [TClass](#tclass-class)'s
name) and each value is a [TClass](#tclass-class) object.

The `.comment` is an optional file-level `str`.

The `.imports` attribute is a possibly empty `dict` where each key is a
`ttype` and where each value is a `str` holding that type's import text.

The `.import_filenames` property is a  utility useful for some UXF
processors. it yields all the unique import filenames.

To create a `Uxf` programmatically (rather than by using, say,
[load()](#load-def), you can either create it empty, or with some data and
optionally, some _ttypes_.

    data = ... # a list, uxf.List, dict, uxf.Map, or uxf.Table
    point_ttype = uxf.TClass('point', (uxf.Field('x', 'real'), uxf.Field('y', 'real')))
    uxo = uxf.Uxf(data, tclasses={point_ttype.ttype: point_ttype})

<a name="Uxf.load-def"></a>
##### .load(filename\_or\_filelike, \*, on\_error=on\_error)

Convenience method that wraps the module-level [load()](#load-def) function.

<a name="Uxf.loads-def"></a>
##### .loads(uxt, filename='-', \*, on\_error=on\_error)

Convenience method that wraps the module-level [loads()](#loads-def)
function.

<a name="Uxf.dump-def"></a>
##### .dump(filename\_or\_filelike, \*, on\_error=on\_error)

Convenience method that wraps the module-level [dump()](#dump-def) function.

<a name="Uxf.dumps-def"></a>
##### .dumps(\*, on\_error=on\_error)

Convenience method that wraps the module-level [dumps()](#dumps-def)
function.

<a name="list-class"></a>
#### List

This class is used to represent a UXF list. It is a `collections.UserList`
subclass that also has `.comment` and `.vtype` attributes.

See [Python UXF Types](#python-uxf-types) for more about _vtypes_.

<a name="map-class"></a>
#### Map

This class is used to represent a UXF map. It is a `collections.UserDict`
subclass that also has `.comment`, `.ktype`, and `.vtype` attributes.

See [Python UXF Types](#python-uxf-types) for more about _ktypes_ and
_vtypes_.

<a name="table-class"></a>
#### Table

This class is used to store UXF Tables. A Table has a
[TClass](#tclass-class) and a `.records` list which is a list of lists of
value with each sublist having the same number of items as the number of
[TClass](#tclass-class) fields. It also has `.comment`, `.ttype` (a
convenience for `.tclass.ttype`), and `.tclass` attributes.

See [Python UXF Types](#python-uxf-types) for more about _ktypes_ and
_ttypes_.

``Table``'s API is very similar to the `list` API, only it works in terms of
whole records rather than individual values.

See also the [table()](#table-def) convenience function.

<a name="tclass-class"></a>
#### TClass

This class is used to store a [Table](#table-class)'s _ttype_ (i.e., its
name) and fields.

The `.ttype` attribute holds the ``TClass``'s name (equivalent to a _vtype_
or _ktype_ name); it may not be the same as a built-in type name or
constant. The `.fields` attribute holds a list of fields of type
[Field](#field-class). The `.comment` holds an optional `str`.

<a name="field-class"></a>
#### Field

This class is used to store a [Table](#table-class)'s fields. The `.name`
must start with a letter and be followed by `0-uxf.MAX_IDENTIFIER_LEN-1`
letters, digits, or underscores; it may not be the same as a built-in type
name or constant. A _vtype_ must be one of these ``str``s: `bool`, `int`,
`real`, `date`, `datetime`, `str`, `bytes`, or `None` (which means accept
any valid type), or a _ttype_ name.

<a name="error-class"></a>
#### Error

This class is used to propagate errors.

(If this module produces an exception that isn't a `uxf.Error` or `IOError`
subclass then it is probably a bug that should be reported.)

### Functions

The functions are documented in importance order. Here are alphabetically
ordered links:
[append\_to\_parent()](#append_to_parent-def),
[canonicalize()](#canonicalize-def),
[dump()](#dump-def),
[dumps()](#dumps-def),
[is\_scalar()](#is_scalar-def),
[load()](#load-def),
[loads()](#loads-def),
[naturalize()](#naturalize-def),
[on\_error()](#on_error-def),
[table()](#table-def).

<a name="load-def"></a>
#### load(filename\_or\_filelike, \*, on\_error=on\_error)

Returns a [Uxf](uxf-class) object.

`filename_or_filelike` is `sys.stdin` or a filename (`str` or
`pathlib.Path`) or an open readable file (text mode UTF-8 encoded,
optionally gzipped).

`on_error` is a custom error handling function that defaults to
[on\_error](#on_error-def).

<a name="loads-def"></a>
#### loads(uxt, filename='-', \*, on\_error=on\_error)

Returns a [Uxf](#uxf-class) object.

`uxt` must be a `str` of UXF data, e.g., `uxf 1.0\n[1 2 3]`.

If given, the `filename` is used for error messages.

For more on the other argument see [load()](#load-def).

<a name="dump-def"></a>
#### dump(filename\_or\_filelike, data, \*, on\_error=on\_error)

`filename_or_filelike` is `sys.stdout` or a filename or an open writable
file (text mode UTF-8 encoded). If `filename_or_filelike` is a filename with
a `.gz` suffix then the output will be gzip-compressed.

`data` is a [Uxf](#uxf-class) object, or a list, [List](#list-class), dict,
[Map](#map-class), or [Table](#table-class), that this function will write
to the `filename_or_filelike` in UXF format.

If the data contains values of types that aren't supported by UXF, they
could either be transformed in advance (e.g., to a custom table type, a
_ttype_).

<a name="dumps-def"></a>
#### dumps(data, \*, on\_error=on\_error)

`data` is a [Uxf](#uxf-class) object, or a list, [List](#list-class), dict,
[Map](#map-class), or [Table](#table-class) that this function will write to
a `str` in UXF format which will then be returned.

For more on the other arguments see [dump()](#dump-def).

<a name="table-def"></a>
#### table(ttype, fields, \*, comment=None)

Convenience function for creating empty tables with a new
[TClass](#tclass-class).

See also the `Table` `__init__()` method.

<a name="naturalize-def"></a>
#### naturalize(s)

Given `str` `s` returns `True` if the `str` is 't', 'true', 'y', 'yes', or
`False` if the `str` is 'f', 'false', 'n', 'no' (case-insensitive); or
returns an `int` if `s` holds a parsable int, or a `float` if `s` holds a
parsable `float`, or a `datetime.datetime` if `s` holds a parsable ISO8601
datetime `str`, or a `datetime.date` if `s` holds a parsable ISO8601 date
`str`, or failing these returns the original `str` `s` unchanged.

This is provided as a helper function (e.g., it is used by `uxfconvert.py`).

<a name="on_error-def"></a>
#### on\_error(lino, code, message, \*, filename, fail=False, verbose=True)

This is the default error handler which you can replace by passing a custom
one to [load()](#load-def), [loads()](#loads-def), [dump()](#dump-def), or
[dumps()](#dumps-def).

This is called with the line number (lino), error code, error message, and
filename. The filename may be '-' or empty if the UXF is created in memory
rather than loaded from a file. If fail is True it means the error is
unrecoverable, so the normal action would be to raise. If verbose is True
the normal action is to print a textual version of the error data to
`stderr`.

For examples of custom `on_error()` functions, see `t/test_errors.py`,
`t/test_imports.py` `t/test_include.py`, `t/test_merge.py`, and
`t/test_sqlite.py`.

<a name="is_scalar-def"></a>
#### is\_scalar(x)

Returns `True` if `x` is `None` or a `bool`, `int`, `float`,
`datetime.date`, `datetime.datetime`, `str`, `bytes`, or `bytearray`;
otherwise returns `False`.

<a name="canonicalize-def"></a>
#### canonicalize(name, is\_table\_name)

Utility for UXF processors. Given a `name`, returns a `name` that is a valid
table or field name. See `uxfconvert.py` for uses.

<a name="append_to_parent-def"></a>
#### append\_to\_parent(parent, value)

Utility for UXF processors; see `uxf.py` and `uxfconvert.py` for examples of
use.

### Constants

|**Constant**|**Description**|
|------------|---------------|
|`VERSION`|The UXF file format version|
|`RESERVED_WORDS`|A set of names that cannot be used for table or field names|

### Command Line Usage

The uxf module can be used as an executable. To see the command line help
run:

    python3 -m uxf -h

or

    path/to/uxf.py -h

---
