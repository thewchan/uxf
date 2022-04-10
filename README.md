# UXF

Uniform eXchange Format (UXF) is a plain text human readable storage
format that may serve as a convenient alternative to csv, ini, json, sqlite,
toml, xml, or yaml.

## Datatypes

UXF supports fourteen datatypes.

|**Type**   |**Example(s) # notes**|
|-----------|----------------------|
|`null`      |`null`|
|`bool`      |`no` `false` `yes` `true`|
|`int`       |`-192` `+234` `7891409`|
|`real`      |`0.15` `0.7e-9` `2245.389` # standard and scientific with at least one digit before and after the point|
|`date`      |`2022-04-01`  # basic ISO8601 YYYY-MM-DD format|
|`datetime`  |`2022-04-01T16:11:51` # ISO8601 (timezone support is library dependent)|
|`str`       |`<Some text which may include newlines>` # using \&lt; for <, \&gt; for >, and \&amp; for &|
|`bytes`     |`(20AC 65 66 48)` # must be even number of case-insensitive hex digits; whitespace optional|
|`ntuple`    | `(:15 14 0 -75:)` # 2-12 numbers (all ``int``s or all ``real``s), e.g., for points, RGB and RGBA numbers, IP addresses, etc.
|`list`      |`[value1 value2 ... valueN]`|
|`map`       |`{key1 value1 key2 value2 ... keyN valueN}`|
|`table`     |`[= <str1> <str2> ... <strN> = <value0_0> ... <value0_N> ... <valueM_0> ... <valueM_N> =]` |

Map keys may only be of types `int`, `date`, `datetime`, `str`, and `bytes`.
(The name we use for a `map` _key-value_ pair is _item_.)

Map and list values may be of _any_ type (including nested ``map``s and
``list``s).

A `table` starts with a table name, then field names, then values. The
number of values in any given row is equal to the number of field names.
(See the examples below).

## Examples

### Minimal empty UXF

    uxf 1.0

### CSV to UXF

#### CSV

    Date,Price,Quantity,ID,Description
    "2022-09-21",3.99,2,"CH1-A2","Chisels (pair), 1in & 1¼in"
    "2022-10-02",4.49,1,"HV2-K9","Hammer, 2lb"
    "2022-10-02",5.89,1,"SX4-D1","Eversure Sealant, 13-floz"

#### UXF equivalents

The most obvious translation would be to a `list` of ``list``s:

    uxf 1.0 Price List
    [
      [<Price List> <Date> <Price> <Quantity> <ID> <Description>]
      [2022-09-21 3.99 2 <CH1-A2> <Chisels (pair), 1in &amp; 1¼in>]
      [2022-10-02 4.49 1 <HV2-K9> <Hammer, 2lb>]
      [2022-10-02 5.89 1 <SX4-D1> <Eversure Sealant, 13-floz>]
    ]

This is perfectly valid. However, it has the same problem of `.csv` files:
is the first row data values or column titles? (For software this isn't
always obvious, for example, if all the values are strings.) Not to mention
the fact that we have to use a nested `list` of ``list``s.

The most _appropriate_ UXF equivalent is to use a UXF `table`:

    uxf 1.0 Price List
    [= <Price List> <Date> <Price> <Quantity> <ID> <Description> =
      2022-09-21 3.99 2 <CH1-A2> <Chisels (pair), 1in &amp; 1¼in> 
      2022-10-02 4.49 1 <HV2-K9> <Hammer, 2lb> 
      2022-10-02 5.89 1 <SX4-D1> <Eversure Sealant, 13-floz> 
    =]

Notice that the _first_ `table` `str` is the name of the table itself, with
the following ``str``s being the field names. Then, after the bare `=` that
separates the names from the values, are the values themselves. There's no
need to group rows into lines (although doing so is common and easier for
human readability), since the UXF processor will know how many values go
into each row based on the number of field names.

Note that if you need to include `&`, `<` or `>` inside a `str`, you
must use the XML/HTML escapes `&amp;`, `&lt;`, and `&gt;` respectively.

### INI to UXF

#### INI

    shapename = Hexagon
    zoom = 150
    showtoolbar = False
    [Window]
    x=615
    y=252
    width=592
    height=636
    scale=1.1
    [Files]
    current=test1.uxf
    recent1=/tmp/test2.uxf
    recent2=C:\Users\mark\test3.uxf

#### UXF equivalents

    uxf 1.0 MyApp 1.2.0 Config
    {
      <General> {
        <shapename> <Hexagon>
        <zoom> 150
        <showtoolbar> no
      }
      <Window> {
        <x> 615
        <y> 252
        <width> 592
        <height> 636
        <scale> 1.1
      }
      <Files> [= <Files> <kind> <filename> =
        <current> <test1.uxf> 
        <recent1> </tmp/test2.uxf> 
        <recent2> <C:\Users\mark\test3.uxf> 
      =]
    }

For configuration data it is often convenient to use ``map``s with name
keys and data values. In this case the overall data is a `map` which
contains each configuration section. The values of each of the first two of
the ``map``'s keys are themselves ``map``s. But for the third key's value
we use a `table`.

Of course, we can nest as deep as we like and mix ``map``s and ``list``s.
For example, here's an alternative:

    uxf 1.0 MyApp 1.2.0 Config
    {
      <General> {
        <shapename> <Hexagon>
        <zoom> 150
        <showtoolbar> no
        <Files> {
          <current> <test1.uxf>
          <recent> [</tmp/test2.uxf> <C:\Users\mark\test3.uxf>]
        }
      }
      <Window> {
        <pos> (:615 252:)
        <size> (:592 636:)
        <scale> 1.1
      }
    }

Here, we've moved the _Files_ into _General_ and changed the _Files_ from a
`table` to a two-item `map` with the second item's value being a `list` of
filenames. We've also changed the _x_, _y_ coordinates and the _width_ and
_height_ into items with `pos` and `size` keys and `ntuple` values. Of
course we could have used a single item with an `ntuple` value, e.g.,
`<geometry> (:615 252 592 636:)`.

### Database to UXF

A database normally consists of one or more tables. A UXF equivalent using
a `list` of ``table``s is easily made.

    uxf 1.0 MyApp Data
    [
      [= <Customers> <CID> <Company> <Address> <Contact> <Email> =
        50 <Best People> <123 Somewhere> <John Doe> <j@doe.com> 
        19 <Supersuppliers> null <Jane Doe> <jane@super.com> 
      =]
      [= <Invoices> <INUM> <CID> <Raised Date> <Due Date> <Paid> <Description> =
        152 50 2022-01-17 2022-02-17 no <COD> 
        153 19 2022-01-19 2022-02-19 yes <> 
      =]
      [= <Items> <IID> <INUM> <Delivery Date> <Unit Price> <Quantity> <Description> =
        1839 152 2022-01-16 29.99 2 <Bales of hay> 
        1840 152 2022-01-16 5.98 3 <Straps> 
        1620 153 2022-01-19 11.5 1 <Washers (1-in)> 
      =]
    ]

Here we have a `list` of ``table``s representing three database tables.

Notice that the second customer has a `null` address and the second
invoice has an empty description.

What if we wanted to add some extra configuration data to the database?

One solution would be to make the first item in the `list` a `map`, with the
remainder ``table``s, as now. Another solution would be to use a `map` for
the container, something like:

    uxf 1.0 MyApp Data
    {
        <config> { <key1> _value1_ ... }
        <tables> [
            _list of tables as above_
        ]
    }

## Libraries

_Implementations in additional languages are planned._

|**Library**|**Language**|**Notes**|
|-----------|------------|---------|
|uxf        | Python 3   | Works out of the box with the standard library, and will use _dateutil_ if available.|

### Python Notes

- Install: `python3 -m pip install uxf`
- Run: `python3 -m uxf -h` _# this shows the command line help_
- Use: `import uxf` _# see the `uxf.py` module docs for the API_

Most Python types map losslessly to and from UXF types. In particular:

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
|`uxf.NTuple`        | `ntuple`   |
|`list`              | `list`     |
|`dict`              | `map`      |
|`uxf.Table`         | `table    `|

If `one_way_conversion` is `False` then any other Python type passed in the
data passed to `write()` will produce an error.

If `one_way_conversion` is `True` then the following conversions are applied
when converting to UXF data:

|**Python Type (in)**|**UXF type/Python Type (out)**|
|--------------------|-------------|
|`bytearray`         | `bytes`     |
|`complex`           | `ntuple`/`uxf.NTuple` _# with two items_|
|`set`               | `list`      |
|`frozenset`         | `list`      |
|`tuple`             | `list`      |
|`collections.deque` | `list`      |

If you have _lots_ of `complex` numbers it may be more compact and
convenient to store them in a two-field table, something like `[=
<Mandelbrot> <real> <imag> = 1.3 3.7 4.9 5.8 ... =]`.

Using `uxf` as an executable (with `python3 -m uxf ...`) provides a means of
doing `.uxf` to `.uxf` conversions (e.g., compress or uncompress, or make
more human readable or more compact).

Installed alongside `uxf.py` is `uxfconvert.py` (from `py/uxfconvert.py`)
which might prove useful to see how to use `uxf`. And also see the
`test/*.uxf` test files.

If you just want to create a small standalone `.pyz`, simply copy
`py/uxf.py` as `uxf.py` into your project folder and inlude it in your
`.pyz` file.

## BNF

A `.uxf` file consists of a mandatory header followed by a single
optional `map`, `list`, or `table`.

    UXF      ::= 'uxf' RWS REAL CUSTOM? '\n' DATA?
    CUSTOM   ::= RWS [^\n]+ # user-defined data e.g. filetype and version
    DATA     ::= (MAP | LIST | TABLE)
    MAP      ::= '{' OWS (KEY RWS ANYVALUE)? (RWS KEY RWS ANYVALUE)* OWS '}'
    LIST     ::= '[' OWS ANYVALUE? (RWS ANYVALUE)* OWS ']'
    TABLE    ::= '[=' (OWS STR){2,} '=' (RWS VALUE)* '=]'
    NTUPLE   ::= '(:' (OWS INT) (RWS INT){1,11} OWS ':)'   # 2-12 ints or
              |  '(:' (OWS REAL) (RWS REAL){1,11} OWS ':)' # 2-12 floats
    KEY      ::= (INT | DATE | DATETIME | STR | BYTES)
    ANYVALUE ::= (VALUE | LIST | MAP | TABLE | NTUPLE)
    VALUE    ::= (NULL | BOOL | INT | REAL | DATE | DATETIME | STR | BYTES)
    NULL     ::= 'null'
    BOOL     ::= 'no' | 'false' | 'yes' | 'true'
    INT      ::= /[-+]?\d+/
    REAL     ::= # standard or scientific (but must contain decimal point)
    DATE     ::= /\d\d\d\d-\d\d-\d\d/ # basic ISO8601 YYYY-MM-DD format
    DATETIME ::= /\d\d\d\d-\d\d-\d\dT\d\d:\d\d(:\d\d)?(Z|[-+]\d\d(:?[:]?\d\d)?)?/ # see note below
    STR      ::= /[<][^<>]*[>]/ # newlines allowed, and &amp; &lt; &gt; supported i.e., XML
    BYTES    ::= '(' (OWS [A-Fa-f0-9]{2})* OWS ')'
    OWS      ::= /[\s\n]*/
    RWS      ::= /[\s\n]+/ # in some cases RWS is actually optional

For a `table` the first `str` is the table's name and the second and
subsequent strings are field names. After the bare `=` come the table's
values. There's no need to distinguish between one row and the next
(although it is common to start new rows on new lines) since the number
of fields indicate how many values each row has.

As the BNF shows, `map` and `list` values may be of _any_ type.

However, `table` values may only be scalars (i.e., of type `null`, `bool`,
`int`, `real`, `date`, `datetime`, `str`, or `bytes`), not ``map``s,
``list``s, ``ntuple``s or ``table``s.

For ``datetime``s, support may vary across different UXF libraries and
might _not_ include timezone support. For example, the Python library
only supports timezones as time offsets; for `Z` etc, the `dateutil`
module must be installed, but even that doesn't necessarily support the full
ISO8601 specification.

Note that a UXF reader (writer) must be able to read (write) a plain text
_or_ gzipped plain text `.uxf` file containing UTF-8 encoded text.

Note also that UXF readers and writers should not care about the actual file
extension since users are free to use their own.

UXF logo ![uxf logo](uxf.svg)

