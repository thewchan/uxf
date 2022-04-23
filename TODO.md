# TODOS

- Since we now have a Utf class add support for a file-level comment, e.g.,
        uxf 1.0 ....
        #<This is an optional file level comment>
        ... optional ttypes ...
        ... map or list or table ...
  - implement for UXF (uxf.py) and for JSON (uxfconvert.py)
  - add to some t/\*.uxf for testing
  - update docs (e.g., include in one shown example, & update BNF)

- Writer → Writer2 & create new Writer
    - map|list|table:
	{COMMENT ktype vtype values}
	{COMMENT ktype values}
	{COMMENT values}
	{ktype vtype values}
	{ktype values}
	{values}
	[COMMENT vtype values]
	[vtype values]
	[values]
	(COMMENT ttype values)
	(ttype values)
    - treat empty and one item maps lists & tables as scalars
    - ∴ add `@property\ndef is_scalar(self)` to Map and List
    - so should only need two methods: write\_collection() and write\_one()

- SQLite (see paper notes)
    - test uxf to sqlite: t2.uxf t4.uxf t15.uxf t22.uxf t24.uxf t35.uxf
    - sqlite\_to\_uxf
    - test sqlite to uxf: t2.sqlite t4.sqlite t15.sqlite (should round trip)

- XML (see paper notes)
    - uxf\_to\_xml: same tests as JSON for full round trip
    - xml\_to\_uxf: same tests as JSON for full round trip

- make sure all test files have some nulls (`?`s) (for every typed value),
  esp. t4, t24, t34

- implement and test all typecheck() methods
  - Add test t40.uxf that exercises all fixtypes in each of a
    list, map, and table
    (i.e., any→str, int↔float, str→bool|int|float|date|datetime|Pair|MyType)
  - Add test t41.uxf ... one for every fixtype that cannot work
  - Do 3 lots of tests covering built-in vtypes and TTypes: for t40.uxf ...:
      * no check, no fixtypes
      * check, no fixtypes
      * check, fixtypes

```
# TODO these are part of the typecheck()ing functionality and may need
# reworking/rethinking in the light of nested collections and ttypes.

def _name_for_type(vtype):
    return {bool: 'bool', bytearray: 'bytes', bytes: 'bytes',
            datetime.date: 'date', datetime.datetime: 'datetime',
            float: 'real', int: 'int', List: 'list', Map: 'map',
            str: 'str', Table: 'table', type(None): '?'}.get(vtype)


def _type_for_name(typename):
    return dict(bool=bool, bytes=(bytes, bytearray), date=datetime.date,
                datetime=datetime.datetime, int=int, list=List, map=Map,
                real=float, str=str, table=Table).get(typename)


def _maybe_fixtype(value, vtype, *, fixtypes=False):
    # TODO rework/rethink in the light of nested collections and ttypes?
    '''Returns value (possibly fixed), fixed (bool), err (None or Error)'''
    if (vtype is None or value is None or isinstance(value, vtype)):
        return value, False, None
    if fixtypes:
        new_value, fixed = _try_fixtype(value, vtype)
        if fixed:
            return new_value, True, None
    expected = _name_for_type(vtype)
    actual = _name_for_type(type(value))
    raise Error(f'expected value of type {expected}, got value '
                f'{value!r} of type {actual}')


def _try_fixtype(value, outtype):
    # TODO rework/rethink in the light of nested collections and ttypes?
    if isinstance(outtype, str):
        return str(value), True
    vclass = type(value)
    if isinstance(vclass, str) and isinstance(outtype, (
            bool, int, float, datetime.date, datetime.datetime)):
        new_value = naturalize(value)
        return new_value, isinstance(new_value, outtype)
    if isinstance(vclass, int) and isinstance(outtype, float):
        return float(value), True
    if isinstance(vclass, float) and isinstance(outtype, int):
        return int(value), True
    return value, False
```

- create tests t50.uxf ... one for every error or warning that uxf.py
  can produce to ensure they all work & are understandable.

- UXF libraries
    - for .js use Dart or TypeScript or similar that can output JS
    - uxf.rs uxf.cpp uxf.java uxf.rb ...

- Uniform eXchange Format - a 7"x9" PDF book? (see paper notes)

# IDEAS

- port my python apps to use UXF (e.g., instead of ini, SQLite, & custom
  formats)
- port my Rust apps to use UXF (e.g., instead of ini, SQLite, & custom
  formats), once I have a Rust UXF library
- experiment with using uxf format to store various kinds of data,
  e.g., styled text, spreadsheet, graphics, etc.
