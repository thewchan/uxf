# UXF

Uniform eXchange Format (UXF) is a plain text human readable optionally
typed storage format. UXF may serve as a convenient alternative to csv, ini,
json, sqlite, toml, xml, or yaml.

UXF is an open standard. The UXF software linked from this page is all free
open source software.

- [Datatypes](#datatypes)
- [Examples](#examples)
- [Libraries](#libraries): [Python](#python)
- [BNF](#bnf)
- [Vim Support](#vim-support)
- [UXF Logo](#uxf-logo)

## Datatypes

Every `.uxf` file consists of a header line (starting `uxf 1.0`), then any
_TType_ (table type) definitions, and then a single `map`, `list`, or
`table` in which all the values are stored. Since ``map``s and ``list``s can
be nested inside each other, the UXF format is extremely flexible.

UXF supports eleven datatypes.

|**Type**   |**Example(s)**|**Notes**|
|-----------|----------------------|--|
|`null`     |`null`||
|`bool`     |`no` `false` `yes` `true`||
|`int`      |`-192` `+234` `7891409`||
|`real`     |`0.15` `0.7e-9` `2245.389`|Standard and scientific with at least one digit before and after the point.|
|`date`     |`2022-04-01`|Basic ISO8601 YYYY-MM-DD format.|
|`datetime` |`2022-04-01T16:11:51`|ISO8601 YYYY-MM-DDTHH:MM:SS format (timezone support is library dependent).|
|`str`      |`<Some text which may include newlines>`|For &, <, >, use \&amp;, \&lt;, \&gt; respectively.|
|`bytes`    |`(:20AC 65 66 48:)`|There must be an even number of case-insensitive hex digits; whitespace optional.|
|`list`     |`[value1 value2 ... valueN]`|A list of values of any type.|
|`list`     |`[vtype value1 value2 ... valueN]`|A list of values of type _vtype_.|
|`map`      |`{key1 value1 key2 value2 ... keyN valueN}`|A map with keys of any valid key type and values of any type.|
|`map`      |`{ktype key1 value1 key2 value2 ... keyN valueN}`|A map with keys of type _ktype_ and values of any type.|
|`map`      |`{ktype vtype key1 value1 key2 value2 ... keyN valueN}`|A map with keys of type _ktype_ and values of type _vtype_.|
|`table`    |`(TType <value0_0> ... <value0_N> ... <valueM_0> ... <valueM_N>)`|A table of values. Each value's type must be of the corresponding type specified in the _TType_, or any table value type where no type has been specified.|

Map keys may only be of types `int`, `date`, `datetime`, `str`, and `bytes`.

Map and list values may be of _any_ type (including nested ``map``s and
``list``s), unless restricted to a specified type.

A `table` starts with a _TType_. Next comes the table's values. The number
of values in any given row is equal to the number of field names in the
_TType_. Values must be of the type specified in the _TType_, or where not
specified, may be of types `bool`, `int`, `real`, `date`, `datetime`, `str`,
or `bytes`. Or the value can be `null`. (See the examples below).

Maps, lists, and tables may begin with a comment, and may optionally by
typed as indicated above. (See also the examples below and the BNF at the end).

Strings may not include `&`, `<` or `>`, so if they are required, we must
use the XML/HTML escapes `&amp;`, `&lt;`, and `&gt;` respectively in their
place.

Where whitespace is allowed (or required) it may be spaces, tabs, or
newlines.

If you don't want to be committed to a particular UXF type, just use a `str`
and do whatever conversion you want.

### Terminolgy

- A `map` _key-value_ is collectively called an _item_.
- A “single” valued type (`bool`, `int`, `str`, `bytes`, `date`,
  `datetime`), is called a _scalar_.
- A `map`, `list`, or `table` which contains only scalar values is called a
  scalar `map`, scalar `list`, or scalar `table`, respectively.

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

    uxf 1.0
    [
      [<Price List> <Date> <Price> <Quantity> <ID> <Description>]
      [2022-09-21 3.99 2 <CH1-A2> <Chisels (pair), 1in &amp; 1¼in>]
      [2022-10-02 4.49 1 <HV2-K9> <Hammer, 2lb>]
      [2022-10-02 5.89 1 <SX4-D1> <Eversure Sealant, 13-floz>]
    ]

This is perfectly valid. However, it has the same problem as `.csv` files:
is the first row data values or column titles? (For software this isn't
always obvious, for example, if all the values are strings.) Not to mention
the fact that we have to use a nested `list` of ``list``s. Nonetheless it is
an improvement, since unlike the `.csv` representation, every value has a
concrete type (all ``str``s for the first row, and `date`, `real`, `int`,
`str`, `str`, for the rest).

The most _appropriate_ UXF equivalent is to use a UXF `table`:

    uxf 1.0
    = PriceList Date Price Quantity ID Description
    (PriceList
      2022-09-21 3.99 2 <CH1-A2> <Chisels (pair), 1in &amp; 1¼in> 
      2022-10-02 4.49 1 <HV2-K9> <Hammer, 2lb> 
      2022-10-02 5.89 1 <SX4-D1> <Eversure Sealant, 13-floz> 
    )

When one or more tables are used each one's _TType_ (table type) must be
defined at the start of the `.uxf` file. A _TType_ begins with an `=` sign
followed by a table name, followed by one or more fields. A field consists
of a name optionally followed by a type (here only names are given). Both
table and field names are user chosen and must consist of an initial capital
letter followed by 0-79 letters, digits, or underscores. (If whitespace is
wanted one convention is to use underscores in their place.)

Once we have a _TType_ we can use it.

Here, we've created a single table whose _TType_ is "PriceList". There's no
need to group rows into lines as we've done here (although doing so is
common and easier for human readability), since the UXF processor knows how
many values go into each row based on the number of field names. In this
example, the UXF processor will treat every five values as a single record
(row) since the _TType_ has five fields.

    uxf 1.0 Price List
    = PriceList Date date Price real Quantity int ID str Description str
    (PriceList
      2022-09-21 3.99 2 <CH1-A2> <Chisels (pair), 1in &amp; 1¼in> 
      2022-10-02 4.49 1 <HV2-K9> <Hammer, 2lb> 
      2022-10-02 5.89 1 <SX4-D1> <Eversure Sealant, 13-floz> 
    )

Here we've added a custom file description in the header, and we've also
added field types to the _TType_ definition. When types are specified, the
UXF processor is expected to be able to check that each value is of the
correct type. Omit the type altogether (as in the earliler examples) to
indicate _any_ valid table type.

### INI to UXF

#### INI

    shapename = Hexagon
    zoom = 150
    showtoolbar = False
    [Window1]
    x=615
    y=252
    width=592
    height=636
    scale=1.1
    [Window2]
    x=28
    y=42
    width=140
    height=81
    scale=1.0
    [Window3]
    x=57
    y=98
    width=89
    height=22
    scale=0.5
    [Files]
    current=test1.uxf
    recent1=/tmp/test2.uxf
    recent2=C:\Users\mark\test3.uxf

#### UXF equivalents

This first equivalent is a simplistic conversion that we'll improve in
stages.

    uxf 1.0 MyApp 1.2.0 Config
    = Files Kind Filename
    {
      <General> {
        <shapename> <Hexagon>
        <zoom> 150
        <showtoolbar> no
      }
      <Window1> {
        <x> 615
        <y> 252
        <width> 592
        <height> 636
        <scale> 1.1
      }
      <Window2> {
        <x> 28
        <y> 42
        <width> 140
        <height> 81
        <scale> 1.0
      }
      <Window3> {
        <x> 57
        <y> 98
        <width> 89
        <height> 22
        <scale> 0.5
      }
      <Files> (Files
        <current> <test1.uxf> 
        <recent1> </tmp/test2.uxf> 
        <recent2> <C:\Users\mark\test3.uxf> 
      )
    }

UXF accepts both `no` and `false` for `bool` `false` and `yes` and `true`
for `bool` `true`. We tend to use `no` and `yes` since they're shorter. (`0`
and `1` cannot be used as ``bool``s since the UXF processor would interpret
them as ``int``s.)

For configuration data it is often convenient to use ``map``s with name
keys and data values. In this case the overall data is a `map` which
contains each configuration section. The values of each of the first two of
the ``map``'s keys are themselves ``map``s. But for the third key's value
we use a `table`. The table's _TType_ is defined at the start and consists
of two untyped fields.

Of course, we can nest as deep as we like and mix ``map``s and ``list``s.
For example, here's an alternative:

    uxf 1.0 MyApp 1.2.0 Config
    = Pos X int Y int
    = Size Width int Height int
    {
      <General> { #<Miscellaneous settings>
        <shapename> <Hexagon> <zoom> 150 <showtoolbar> no <Files> {
          <current> <test1.uxf>
          <recent> [ #<From most to least recent>
          </tmp/test2.uxf> <C:\Users\mark\test3.uxf>]
        }
      }
      <Window1> { #<Window dimensions and scales> str
        <pos> (Pos 615 252)
        <size> (Size 592 636)
        <scale> 1.1
      }
      <Window2> {
        <pos> (Pos 28 42)
        <size> (Size 140 81)
        <scale> 1.0
      }
      <Window3> {
        <pos> (Pos 57 98)
        <size> (Size 89 22)
        <scale> 0.5
      }
    }

Here, we've laid out the _General_ and _Window_ maps more compactly. We've
also moved the _Files_ into _General_ and changed the _Files_ from a `table`
to a two-item `map` with the second item's value being a `list` of
filenames. We've also changed the _x_, _y_ coordinates and the _width_ and
_height_ into "Pos" and "Size" tables. Notice that for each of these tables
we've defined their _TType_ to include both field names and types.

We've also added some example comments to two of the ``map``s. A comment is
a `#` immediately followed by a `str`. A comment may only be placed at the
start of a list before the optional _vtype_ or the first value, or at the
start of a map before the optional _ktype_ or the first key, or at the start
of a table before the _TType_ name.

    uxf 1.0 MyApp 1.2.0 Config
    = Pos X int Y int
    = Size Width int Height int
    { #<Notes on this configuration file format> str map
      <General> { #<Miscellaneous settings> str
        <shapename> <Hexagon> <zoom> 150 <showtoolbar> no <Files> { str
          <current> <test1.uxf>
          <recent> [ #<From most to least recent> str
          </tmp/test2.uxf> <C:\Users\mark\test3.uxf>]
        }
      }
      <Windows> { #<Window dimensions and scales>
        <pos> (Pos 615 252 28 42 57 98)
        <size> (Size 592 636 140 81 89 22)
        <scale> [1.1 1.0 0.5]
      }
    }

Here we've added some types. The outermost map must have `str` keys and
`map` values, and the _General_, _Files_, and _Window_ maps must all have
`str` keys and _any_ values. For ``map``s we may specify the key and
value types, or just the key type, or neither. We've also specified that the
_recent_ files ``list``'s values must be ``str``s.

Notice that instead of individual "Windows" entries we've just used one.
Since "Pos" and "Size" are tables they can have as many rows as we like, in
this case three (since each row has two fields based on each table's
_TType_).

    uxf 1.0 MyApp 1.2.0 Config
    = Geometry X int Y int Width int Height int Scale real
    { #<Notes on this configuration file format> str map
      <General> { #<Miscellaneous settings> str
        <shapename> <Hexagon> <zoom> 150 <showtoolbar> no <Files> { str
          <current> <test1.uxf>
          <recent> [ #<From most to least recent> str
          </tmp/test2.uxf> <C:\Users\mark\test3.uxf>]
        }
      }
      <Windows> ( #<Window dimensions and scales> Geometry
         615 252 592 636 1.1
         28 42 140 81 1.0
         57 98 89 22 0.5
      )
    }

For this final variation we've gathered all the window data into a single
table type and laid it out for human readability. We could, of course, have
just written it as `(Geometry 615 252 592 636 1.1 28 42 140 81 1.0 57 98 89
22 0.5)`.

### Database to UXF

A database normally consists of one or more tables. A UXF equivalent using
a `list` of ``table``s is easily made.

    uxf 1.0 MyApp Data
    = Customers CID Company Address Contact Email
    = Invoices INUM CID Raised_Date Due_Date Paid Description
    = Items IID INUM Delivery_Date Unit_Price Quantity Description
    [ #<There is a 1:M relationship between the Invoices and Items tables>
      (Customers
        50 <Best People> <123 Somewhere> <John Doe> <j@doe.com> 
        19 <Supersuppliers> null <Jane Doe> <jane@super.com> 
      )
      (Invoices
        152 50 2022-01-17 2022-02-17 no <COD> 
        153 19 2022-01-19 2022-02-19 yes <> 
      )
      (Items
        1839 152 2022-01-16 29.99 2 <Bales of hay> 
        1840 152 2022-01-16 5.98 3 <Straps> 
        1620 153 2022-01-19 11.5 1 <Washers (1-in)> 
      )
    ]

Here we have a `list` of ``table``s representing three database tables.
The `list` begins with a comment.

Notice that the second customer has a `null` address and the second invoice
has an empty description.

    uxf 1.0 MyApp Data
    = Customers CID int Company str Address str Contact str Email str
    = Invoices INUM int CID int Raised_Date date Due_Date date Paid bool Description str
    = Items IID int INUM int Delivery_Date date Unit_Price real Quantity int Description str
    [ #<There is a 1:M relationship between the Invoices and Items tables>
      (Customers
        50 <Best People> <123 Somewhere> <John Doe> <j@doe.com> 
        19 <Supersuppliers> null <Jane Doe> <jane@super.com> 
      )
      (Invoices
        152 50 2022-01-17 2022-02-17 no <COD> 
        153 19 2022-01-19 2022-02-19 yes <> 
      )
      (Items
        1839 152 2022-01-16 29.99 2 <Bales of hay> 
        1840 152 2022-01-16 5.98 3 <Straps> 
        1620 153 2022-01-19 11.5 1 <Washers (1-in)> 
      )
    ]

Here, we've added types to each table's _TType_.

What if we wanted to add some extra configuration data to the database? One
solution would be to make the first item in the `list` a `map`, with the
remainder ``table``s, as now. Another solution would be to use a `map` for
the container, something like:

    {
        <config> { #<Key-value configuration data goes here> }
        <tables> [ #<The list of tables as above follows here>
            
        ]
    }

## Libraries

_Implementations in additional languages are planned._

|**Library**|**Language**|**Notes**                    |
|-----------|------------|-----------------------------|
|uxf        | Python 3   | See [Python](#python) below.|

### Python

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

If `one_way_conversion` is `False` then any other Python type passed in
the data passed to `write()` will produce an error.

If `one_way_conversion` is `True` then the following conversions are
applied when converting to UXF data:

|**Python Type (in)**|**UXF type**|**Python Type (out)**|
|--------------------|------------|---------------------|
|`bytearray`         | `bytes`    | `bytes`    |
|`set`               | `list`     | `uxf.List` |
|`frozenset`         | `list`     | `uxf.List` |
|`tuple`             | `list`     | `uxf.List` |
|`collections.deque` | `list`     | `uxf.List` |

For complex numbers you could create a _TType_ such as: `= Complex Real real
Imag real`. Then you could include single complex values like `(Complex 1.5
7.2)`, or many of them such as `(Complex 1.5 7.2 8.3 -9.4 14.8 0.6)`.

Using `uxf` as an executable (with `python3 -m uxf ...`) provides a means of
doing `.uxf` to `.uxf` conversions (e.g., compress or uncompress, or make
more human readable or more compact).

Installed alongside `uxf.py` is `uxfconvert.py` (from `py/uxfconvert.py`)
which might prove useful to see how to use `uxf`. For example,
`uxfconvert.py` can convert `.csv`, `.ini` (very basic), and `.sqlite`
(tables only) files into `.uxf`, and can losslessly convert `.uxf` to
`.json` or `.xml` and back. And also see the `t/*` test files.

If you just want to create a small standalone `.pyz`, simply copy
`py/uxf.py` as `uxf.py` into your project folder and inlude it in your
`.pyz` file.

## BNF

A `.uxf` file consists of a mandatory header followed by a single
optional `map`, `list`, or `table`.

    UXF          ::= 'uxf' RWS REAL CUSTOM? '\n' DATA?
    CUSTOM       ::= RWS [^\n]+ # user-defined data e.g. filetype and version
    DATA         ::= TTYPE* (MAP | LIST | TABLE)
    TTYPE        ::= '=' OWS IDENTIFIER (RWS FIELD)+ # IDENTIFIER is table name
    FIELD        ::= IDENTIFIER (RWS VALUETYPE)? # IDENTIFIER is field name
    MAP          ::= '{' COMMENT? MAPTYPES? OWS (KEY RWS ANYVALUE)? (RWS KEY RWS ANYVALUE)* OWS '}'
    MAPTYPES     ::= OWS KEYTYPE (RWS ANYVALUETYPE)?
    KEYTYPE      ::= 'int' | 'date' | 'datetime' | 'str' | 'bytes'
    VALUETYPE    ::= KEYTYPE | 'null' | 'bool' | 'real' 
    ANYVALUETYPE ::= VALUETYPE | 'list' | 'map' | 'table'
    LIST         ::= '[' COMMENT? LISTTYPE? OWS ANYVALUE? (RWS ANYVALUE)* OWS ']'
    LISTTYPE     ::= OWS ANYVALUETYPE
    TABLE        ::= '(' COMMENT? OWS IDENTIFIER (RWS VALUE)* ')' # IDENTIFIER is TTYPE name
    COMMENT      ::= OWS '#' STR
    KEY          ::= INT | DATE | DATETIME | STR | BYTES
    VALUE        ::= KEY | NULL | BOOL | REAL
    ANYVALUE     ::= VALUE | LIST | MAP | TABLE
    NULL         ::= 'null'
    BOOL         ::= 'no' | 'false' | 'yes' | 'true'
    INT          ::= /[-+]?\d+/
    REAL         ::= # standard or scientific (but must contain decimal point)
    DATE         ::= /\d\d\d\d-\d\d-\d\d/ # basic ISO8601 YYYY-MM-DD format
    DATETIME     ::= /\d\d\d\d-\d\d-\d\dT\d\d:\d\d(:\d\d)?(Z|[-+]\d\d(:?[:]?\d\d)?)?/ # see note below
    STR          ::= /[<][^<>]*?[>]/ # newlines allowed, and &amp; &lt; &gt; supported i.e., XML
    BYTES        ::= '(:' (OWS [A-Fa-f0-9]{2})* OWS ':)'
    IDENTIFIER   ::= /\p{Lu}\w{0,79}/ # Must start with an uppercase letter
    OWS          ::= /[\s\n]*/
    RWS          ::= /[\s\n]+/ # in some cases RWS is actually optional

To indicate any type valid for the context, simply omit the type name.

As the BNF shows, `map` and `list` values may be of _any_ type including
nested ``map``s and ``list``s.

For a `table`, after the optional comment, is an identifier which is the
table's _TType_. This is followed by the table's values. There's no need to
distinguish between one row and the next (although it is common to start new
rows on new lines) since the number of fields indicate how many values each
row has.

Notice that `table` values may only be scalars (i.e., the literal `null`, or
of type `bool`, `int`, `real`, `date`, `datetime`, `str`, or `bytes`), not
``map``s, ``list``s, or ``table``s.

If a map key, list value, or table value's type is specified, then the UXF
processor is expected to be able to check for (and if requested and
possible, correct) any mistyped values.

For ``datetime``s, support may vary across different UXF libraries and
might _not_ include timezone support. For example, the Python library
only supports timezones as time offsets; for `Z` etc, the `dateutil`
module must be installed, but even that doesn't necessarily support the full
ISO8601 specification.

Note that a UXF reader (writer) must be able to read (write) a plain text
_or_ gzipped plain text `.uxf` file containing UTF-8 encoded text.

Note also that UXF readers and writers should not care about the actual file
extension since users are free to use their own.

## Vim Support

If you use the vim editor, simple color syntax highlighting is available.
Copy `uxf.vim` into your `$VIM/syntax/` folder and add this line (or
similar) to your `.vimrc` or `.gvimrc` file:

    au BufRead,BufNewFile,BufEnter *.uxf set ft=uxf|set expandtab|set tabstop=2|set softtabstop=2|set shiftwidth=2

## UXF Logo

![uxf logo](uxf.svg)
