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

UXF supports fourteen datatypes.

|**Type**   |**Example(s)**|**Notes**|
|-----------|----------------------|--|
|`null`     |`null`||
|`bool`     |`no` `false` `yes` `true`||
|`int`      |`-192` `+234` `7891409`||
|`real`     |`0.15` `0.7e-9` `2245.389`|standard and scientific with at least one digit before and after the point|
|`date`     |`2022-04-01`| basic ISO8601 YYYY-MM-DD format|
|`datetime` |`2022-04-01T16:11:51`|ISO8601 YYYY-MM-DDTHH:MM:SS format (timezone support is library dependent)|
|`str`      |`<Some text which may include newlines>`|for &, <, >, use \&amp;, \&lt;, \&gt; respectively|
|`bytes`    |`(:20AC 65 66 48:)`|must have an even number of case-insensitive hex digits; whitespace optional|
|`list`     |`[value1 value2 ... valueN]`|a list of values of any type
|`list`     |`[type value1 value2 ... valueN]`|a list of values of type _type_
|`map`      |`{key1 value1 key2 value2 ... keyN valueN}`|a map with keys of any valid key type and values of any type|
|`map`      |`{ktype key1 value1 key2 value2 ... keyN valueN}`|a map with keys of type _ktype_ and values of any type|
|`map`      |`{ktype vtype key1 value1 key2 value2 ... keyN valueN}`|a map with keys of type _ktype_ and values of type _vtype_|
|`table`    |`( TType <value0_0> ... <value0_N> ... <valueM_0> ... <valueM_N> )`|values must by of the corresponding type specified in the _TType_, or any table value type where no type is specified

Map keys may only be of types `int`, `date`, `datetime`, `str`, and `bytes`.
(The name we use for a `map` _key-value_ pair is _item_.)

Map and list values may be of _any_ type (including nested ``map``s and
``list``s).

A `table` starts with a [_TType_](#ttype). Next comes the table's values.
The number of values in any given row is equal to the number of field names
in the _TType_. Values must be of the type specified in the _TType_, or
where not specified, may be of types `bool`, `int`, `real`, `date`,
`datetime`, `str`, `bytes`. Or the value can be `null`. (See the examples
below).

Maps, lists, and tables may begin with a comment, and may optionally by
typed as indicated above. (See also the examples below and the BNF at the end).

Where whitespace is allowed (or required) it may be spaces, tabs, or
newlines.

If you don't want to be committed to a particular UXF type, just use a `str`
and do whatever conversion you want.

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
the fact that we have to use a nested `list` of ``list``s.

The most _appropriate_ UXF equivalent is to use a UXF `table`:

    uxf 1.0 Price List
    = PriceList <Date> <Price> <Quantity> <ID> <Description>
    ( PriceList
      2022-09-21 3.99 2 <CH1-A2> <Chisels (pair), 1in &amp; 1¼in> 
      2022-10-02 4.49 1 <HV2-K9> <Hammer, 2lb> 
      2022-10-02 5.89 1 <SX4-D1> <Eversure Sealant, 13-floz> 
    )

######################### TODO UPDATE THE TEXT FOR TTYPES #############################

Here we begin by identifying the custom data our `.uxf` file contains by
providing some descriptive text after the UXF introduction (`uxf 1.0`).

Notice that the _first_ `table` `str` is the name of the table itself, with
the following ``str``s being the field names. Then, after the bare `=` that
separates the names from the values, are the values themselves. There's no
need to group rows into lines (although doing so is common and easier for
human readability), since the UXF processor will know how many values go
into each row based on the number of field names.

    uxf 1.0 Price List
    = PriceList <Date> date <Price> real <Quantity> int <ID> str <Description> str
    ( PriceList
      2022-09-21 3.99 2 <CH1-A2> <Chisels (pair), 1in &amp; 1¼in> 
      2022-10-02 4.49 1 <HV2-K9> <Hammer, 2lb> 
      2022-10-02 5.89 1 <SX4-D1> <Eversure Sealant, 13-floz> 
    )

Here we've added field (column) types: if specified the UXF processor is
expected to be able to check that each value is of the correct type. Omit
the type altogether to indicate _any_ valid type.

Note that if you need to include `&`, `<` or `>` inside a `str`, you
must use the XML/HTML escapes `&amp;`, `&lt;`, and `&gt;` respectively.

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

    uxf 1.0 MyApp 1.2.0 Config
    = Files <kind> <filename>
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
      <Files> ( Files
        <current> <test1.uxf> 
        <recent1> </tmp/test2.uxf> 
        <recent2> <C:\Users\mark\test3.uxf> 
      )
    }

UXF accepts both `no` and `false` for `bool` `false` and `yes` and `true`
for `bool` `true`. We tend to use `no` and `yes` since they're shorter. (`0`
and `1` can't be used as ``bool``s since the UXF processor would interpret
them as ``int``s.)

For configuration data it is often convenient to use ``map``s with name
keys and data values. In this case the overall data is a `map` which
contains each configuration section. The values of each of the first two of
the ``map``'s keys are themselves ``map``s. But for the third key's value
we use a `table`.

Of course, we can nest as deep as we like and mix ``map``s and ``list``s.
For example, here's an alternative:

    uxf 1.0 MyApp 1.2.0 Config
    = Pos <x> int <y> int
    = Size <width> int <height> int
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
_height_ into items with `pos` and `size` keys and table values. Of
course we could have used a single item with an table value, e.g.,
`<geometry> (:615 252 592 636:)`.

Here we've added some example comments to two ``map``s and a `list`. A
comment is a `#` immediately followed by a `str`. As usual for UXF, the
`str` must not contain &, <, > characters, but instead use the XML/HTML
escapes.

Comments may only be placed at the start of a `map`, `list`, or `table`.
Since every `.uxf` file holds _one_ overarching `list`, `map`, or `table`
containing all the other data, this makes it easy to add an overall comment
at the beginning of the file.

    uxf 1.0 MyApp 1.2.0 Config
    = Pos <x> int <y> int
    = Size <width> int <height> int
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

### Database to UXF

A database normally consists of one or more tables. A UXF equivalent using
a `list` of ``table``s is easily made.

    uxf 1.0 MyApp Data
    = Customers <CID> <Company> <Address> <Contact> <Email>
    = Invoices <INUM> <CID> <Raised Date> <Due Date> <Paid> <Description>
    = Items <IID> <INUM> <Delivery Date> <Unit Price> <Quantity> <Description>
    [ #<There is a 1:M relationship between the Invoices and Items tables>
      ( Customers
        50 <Best People> <123 Somewhere> <John Doe> <j@doe.com> 
        19 <Supersuppliers> null <Jane Doe> <jane@super.com> 
      )
      ( Invoices
        152 50 2022-01-17 2022-02-17 no <COD> 
        153 19 2022-01-19 2022-02-19 yes <> 
      )
      ( Items
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
    = Customers <CID> int <Company> str <Address> str <Contact> str <Email> str
    = Invoices <INUM> int <CID> int <Raised Date> date <Due Date> date <Paid> bool <Description> str
    = Items <IID> int <INUM> int <Delivery Date> date <Unit Price> real <Quantity> int <Description> str
    [ #<There is a 1:M relationship between the Invoices and Items tables>
      ( Customers
        50 <Best People> <123 Somewhere> <John Doe> <j@doe.com> 
        19 <Supersuppliers> null <Jane Doe> <jane@super.com> 
      )
      ( Invoices
        152 50 2022-01-17 2022-02-17 no <COD> 
        153 19 2022-01-19 2022-02-19 yes <> 
      )
      ( Items
        1839 152 2022-01-16 29.99 2 <Bales of hay> 
        1840 152 2022-01-16 5.98 3 <Straps> 
        1620 153 2022-01-19 11.5 1 <Washers (1-in)> 
      )
    ]

Here, we've added types to each of the tables.

What if we wanted to add some extra configuration data to the database? One
solution would be to make the first item in the `list` a `map`, with the
remainder ``table``s, as now. Another solution would be to use a `map` for
the container, something like:

    uxf 1.0 MyApp Data
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

For complex numbers you could create a _TType_ such as:

    = Complex Real real Imag real

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
    MAP          ::= '{' COMMENT? MAPTYPES? OWS (KEY RWS ANYVALUE)? (RWS KEY RWS ANYVALUE)* OWS '}'
    MAPTYPES     ::= OWS KEYTYPE (RWS ANYVALUETYPE)?
    KEYTYPE      ::= 'int' | 'date' | 'datetime' | 'str' | 'bytes'
    VALUETYPE    ::= KEYTYPE | 'null' | 'bool' | 'real' 
    ANYVALUETYPE ::= VALUETYPE | 'list' | 'map' | 'table'
    LIST         ::= '[' COMMENT? LISTTYPE? OWS ANYVALUE? (RWS ANYVALUE)* OWS ']'
    LISTTYPE     ::= OWS ANYVALUETYPE
    TTYPE        ::= '=' OWS IDENTIFIER (RWS FIELD)+ # IDENTIFIER is table name
    FIELD        ::= IDENTIFIER (RWS VALUETYPE)? # IDENTIFIER is field name
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
    STR          ::= /[<][^<>]*[>]/ # newlines allowed, and &amp; &lt; &gt; supported i.e., XML
    BYTES        ::= '(:' (OWS [A-Fa-f0-9]{2})* OWS ':)'
    IDENTIFIER   ::= /\p{Lu}\w*/ # Must start with an uppercase letter
    OWS          ::= /[\s\n]*/
    RWS          ::= /[\s\n]+/ # in some cases RWS is actually optional

To indicate any type valid for the context, simply omit the type name.

As the BNF shows, `map` and `list` values may be of _any_ type.

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
