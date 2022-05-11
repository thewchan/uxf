# Python UXF Library

For details of the Uniform eXchange Format (UXF) supported by this library,
see the [UXF Overview](../README.md). ([PyPI link to UXF
Overview](https://github.com/mark-summerfield/uxf/blob/main/README.md).)

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

For complex numbers you could create a _ttype_ such as: `= Complex Real real
Imag real`. Then you could include single complex values like `(Complex 1.5
7.2)`, or many of them such as `(Complex 1.5 7.2 8.3 -9.4 14.8 0.6)`.

For custom types (e.g., enums; or as an alternative to using a _ttype_ for
complex numbers, or for any other custom type), use `uxf.add_converter()`.
See `test_converters.py` for examples.

For collection types such as `set`, `frozenset`, `tuple`, or
`collections.deque`, either manually convert to/from a `List`, or set
`uxf.AutoConvertSequences = True`, in which case any of these will be
automatically converted to a `List` when they are encountered. Of course,
these are one way conversions.

Using `uxf` as an executable (with `python3 -m uxf ...`) provides a means of
doing `.uxf` to `.uxf` conversions (e.g., compress or uncompress, or make
more human readable or more compact).

Installed alongside `uxf.py` is `uxfconvert.py` which might prove useful to
see how to use `uxf`. For example, `uxfconvert.py` can losslessly convert
`.uxf` to `.json` or `.xml` and back. It can also do some simple conversions
to and from `.csv`, to `.ini`, and to and from `.sqlite`, but these are
really to illustrate use of the uxf APIs. And also see the `../t/*` test
files and the `../eg` folder (for example, the `../eg/slides.uxf` and
`../eg/slides.py` files).

If you just want to create a small standalone `.pyz`, simply copy
`py/uxf.py` as `uxf.py` into your project folder and inlude it in your
`.pyz` file.
