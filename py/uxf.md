<table>
<tbody>
<tr class="odd">
<td> <br />
 <br />
<strong>uxf</strong> (version 0.30.0)</td>
<td style="text-align: right;"><a href=".">index</a><br />
<a href="file:/home/mark/app/uxf/py/uxf.py">/home/mark/app/uxf/py/uxf.py</a></td>
</tr>
</tbody>
</table>

`UXF is a plain text human readable optionally typed storage format. UXF may
serve as a convenient alternative to csv, ini, json, sqlite, toml, xml, or
yaml.  
The uxf module can be used as an executable. To see the command line help run:
      python3 -m uxf -h   or       path/to/uxf.py -h  
The uxf module distinguishes between a ttype (the name of a user-defined
table) and a TClass (the Python class which represents a user-defined
table). A TClass has a .ttype attribute and a .fields attribute (see below).
  The uxf module's public API provides the following free functions and
classes.       load(filename_or_filelike): -> uxo     loads(uxt): -> uxo
  These functions read UXF data from a file, file-like, or string.
The returned uxo is of type Uxf (see below).
See the function docs for additional options.  
In the docs we use uxo to refer to a Uxf object and uxt to refer to a string
containing a UXF file's text.       dump(filename_or_filelike, data)
    dumps(data) -> uxt  
These functions write UXF data to a file, file-like, or string.
The data can be a Uxf object or a single list, List, dict, Map, or Table.
dump() writes the data to the filename_or_filelike; dumps() writes the data
into a string that's then returned. See the function docs for additional
options.       on_error(...)  
This is the default error handler which you can replace by passing a new one
to load(s) and dump(s). For examples of custom on_error functions, see
t/test_errors.py and eg/on_error.py.  
    add_converter(obj_type, to_str, from_str)  
This function can be used to register custom types and custom converters
to/from strings. (See test_converter.py examples of use.)  
    naturalize(s) -> object  
This function takes a str and returns a bool or datetime.datetime or
datetime.date or int or float if any of these can be parsed, otherwise
returns the original string s. This is provided as a helper function (e.g.,
it is used by uxfconvert.py).       canonicalize(name)  
Given a name, returns a name that is a valid table or field name.  
    is_scalar(x) -> bool  
Returns True if x is None or a bool, int, float, datetime.date,
datetime.datetime, str, bytes, or bytearray; otherwise returns False.  
    Error   This class is used to propagate errors.  
(If this module produces an exception that isn't a uxf.Error or IOError
subclass then it is probably a bug that should be reported.)       Uxf  
This class has a .data attribute which holds a Map, List, or Table, a
.custom str holding a (possibly empty) custom string, and a .tclasses
holding a (possibly empty) dict whose names are TClass table names (ttypes)
and whose values are TClasses. It also has convenience dump(), dumps(),
load() and loads() methods.       List  
This class is used to represent a UXF list. It is a collections.UserList
subclass that also has .comment and .vtype attributes.       Map  
This class is used to represent a UXF map. It is a collections.UserDict
subclass that also has .comment, .ktype, and .vtype attributes. It also has
a special append() method.       Table  
This class is used to store UXF Tables. A Table has a TClass (see below) and
a records list which is a list of lists of scalars with each sublist having
the same number of items as the number of fields. It also has .comment,
.ttype (a convenience for .tclass.ttype), and .tclass attributes, and a
special append() method. See also the table() convenience function.  
    TClass  
This class is used to store a Table's ttype (i.e., its name) and fields (see
below).       Field  
This class is used to store a Table's fields. The .name must start with a
letter and be followed by 0-uxf.MAX_IDENTIFIER_LEN-1 letters, digits, or
underscores. A vtype must be one of these strs: 'bool', 'int', 'real',
'date', 'datetime', 'str', 'bytes', or None (which means accept any valid
type), or a ttype name.  
Note that for imports, if the filename is relative it is searched for in the
same folder as the importing UXF file, and if not found there, each of the
paths in UXF_PATH is tried in turn (if any).  
Note that the __version__ is the module version (i.e., the versio of this
implementation), while the VERSION is the maximum UXF version that this
module can read (and the UXF version that it writes).`

   
**Modules**

`      `

 

<table>
<tbody>
<tr class="odd">
<td><a href="collections.html">collections</a><br />
<a href="datetime.html">datetime</a><br />
<a href="enum.html">enum</a><br />
</td>
<td><a href="functools.html">functools</a><br />
<a href="gzip.html">gzip</a><br />
<a href="io.html">io</a><br />
</td>
<td><a href="os.html">os</a><br />
<a href="pathlib.html">pathlib</a><br />
<a href="sys.html">sys</a><br />
</td>
<td><a href="urllib.html">urllib</a><br />
</td>
</tr>
</tbody>
</table>

   
**Classes**

`      `

 

[builtins.object](builtins.html#object)

[Field](uxf.html#Field)

[TClass](uxf.html#TClass)

[Table](uxf.html#Table)

[Uxf](uxf.html#Uxf)

[collections.UserDict](collections.html#UserDict)([collections.abc.MutableMapping](collections.abc.html#MutableMapping))

[Map](uxf.html#Map)

[collections.UserList](collections.html#UserList)([collections.abc.MutableSequence](collections.abc.html#MutableSequence))

[List](uxf.html#List)

   
<span id="Field">class
**Field**</span>([builtins.object](builtins.html#object))

`   `

`Field(name, vtype=None)    `

 

Methods defined here:  

  - <span id="Field-__init__">**\_\_init\_\_**</span>(self, name,
    vtype=None)  
    `The type of one field in a Table
    .name holds the field's name (equivalent to a vtype or ktype name);
    may not be the same as a built-in type name or constant
    .vtype holds a UXF type name ('int', 'real', …)`

<!-- end list -->

  - <span id="Field-__repr__">**\_\_repr\_\_**</span>(self)  
    `Return repr(self).`

-----

Data descriptors defined here:  

  - **\_\_dict\_\_**  
    `dictionary for instance variables (if defined)`

<!-- end list -->

  - **\_\_weakref\_\_**  
    `list of weak references to the object (if defined)`

**name**

   
<span id="List">class
**List**</span>([collections.UserList](collections.html#UserList))

`   `

`List(*args, **kwargs)  
A more or less complete user-defined wrapper around list objects. `

 

  - Method resolution order:  
    [List](uxf.html#List)
    [collections.UserList](collections.html#UserList)
    [collections.abc.MutableSequence](collections.abc.html#MutableSequence)
    [collections.abc.Sequence](collections.abc.html#Sequence)
    [collections.abc.Reversible](collections.abc.html#Reversible)
    [collections.abc.Collection](collections.abc.html#Collection)
    [collections.abc.Sized](collections.abc.html#Sized)
    [collections.abc.Iterable](collections.abc.html#Iterable)
    [collections.abc.Container](collections.abc.html#Container)
    [builtins.object](builtins.html#object)

-----

Methods defined here:  

  - <span id="List-__init__">**\_\_init\_\_**</span>(self, \*args,
    \*\*kwargs)  
    `Takes same arguments as list. .data holds the actual list
    .comment holds an optional comment
    .vtype holds a UXF type name ('int', 'real', …)`

-----

Data and other attributes defined here:  

**\_\_abstractmethods\_\_** = frozenset()

-----

Methods inherited from
[collections.UserList](collections.html#UserList):  

<span id="List-__add__">**\_\_add\_\_**</span>(self, other)

<span id="List-__contains__">**\_\_contains\_\_**</span>(self, item)

<span id="List-__copy__">**\_\_copy\_\_**</span>(self)

<span id="List-__delitem__">**\_\_delitem\_\_**</span>(self, i)

  - <span id="List-__eq__">**\_\_eq\_\_**</span>(self, other)  
    `Return self==value.`

<!-- end list -->

  - <span id="List-__ge__">**\_\_ge\_\_**</span>(self, other)  
    `Return self>=value.`

<span id="List-__getitem__">**\_\_getitem\_\_**</span>(self, i)

  - <span id="List-__gt__">**\_\_gt\_\_**</span>(self, other)  
    `Return self>value.`

<span id="List-__iadd__">**\_\_iadd\_\_**</span>(self, other)

<span id="List-__imul__">**\_\_imul\_\_**</span>(self, n)

  - <span id="List-__le__">**\_\_le\_\_**</span>(self, other)  
    `Return self<=value.`

<span id="List-__len__">**\_\_len\_\_**</span>(self)

  - <span id="List-__lt__">**\_\_lt\_\_**</span>(self, other)  
    `Return self<value.`

<span id="List-__mul__">**\_\_mul\_\_**</span>(self, n)

<span id="List-__radd__">**\_\_radd\_\_**</span>(self, other)

  - <span id="List-__repr__">**\_\_repr\_\_**</span>(self)  
    `Return repr(self).`

<span id="List-__rmul__">**\_\_rmul\_\_**</span> =
[\_\_mul\_\_](#List-__mul__)(self, n)

<span id="List-__setitem__">**\_\_setitem\_\_**</span>(self, i, item)

  - <span id="List-append">**append**</span>(self, item)  
    `S.append(value) -- append value to the end of the sequence`

<!-- end list -->

  - <span id="List-clear">**clear**</span>(self)  
    `S.clear() -> None -- remove all items from S`

<span id="List-copy">**copy**</span>(self)

  - <span id="List-count">**count**</span>(self, item)  
    `S.count(value) -> integer -- return number of occurrences of value`

<!-- end list -->

  - <span id="List-extend">**extend**</span>(self, other)  
    `S.extend(iterable) -- extend sequence by appending elements from the iterable`

<!-- end list -->

  - <span id="List-index">**index**</span>(self, item, \*args)  
    `S.index(value, [start, [stop]]) -> integer -- return first index of value.
    Raises ValueError if the value is not present.  
    Supporting start and stop arguments is optional, but recommended.`

<!-- end list -->

  - <span id="List-insert">**insert**</span>(self, i, item)  
    `S.insert(index, value) -- insert value before index`

<!-- end list -->

  - <span id="List-pop">**pop**</span>(self, i=-1)  
    `S.pop([index]) -> item -- remove and return item at index (default last).
    Raise IndexError if list is empty or index is out of range.`

<!-- end list -->

  - <span id="List-remove">**remove**</span>(self, item)  
    `S.remove(value) -- remove first occurrence of value.
    Raise ValueError if the value is not present.`

<!-- end list -->

  - <span id="List-reverse">**reverse**</span>(self)  
    `S.reverse() -- reverse *IN PLACE*`

<span id="List-sort">**sort**</span>(self, /, \*args, \*\*kwds)

-----

Data descriptors inherited from
[collections.UserList](collections.html#UserList):  

  - **\_\_dict\_\_**  
    `dictionary for instance variables (if defined)`

<!-- end list -->

  - **\_\_weakref\_\_**  
    `list of weak references to the object (if defined)`

-----

Data and other attributes inherited from
[collections.UserList](collections.html#UserList):  

**\_\_hash\_\_** = None

-----

Methods inherited from
[collections.abc.Sequence](collections.abc.html#Sequence):  

<span id="List-__iter__">**\_\_iter\_\_**</span>(self)

<span id="List-__reversed__">**\_\_reversed\_\_**</span>(self)

-----

Class methods inherited from
[collections.abc.Reversible](collections.abc.html#Reversible):  

  - <span id="List-__subclasshook__">**\_\_subclasshook\_\_**</span>(C)
    from [abc.ABCMeta](abc.html#ABCMeta)  
    `Abstract classes can override this to customize issubclass().  
    This is invoked early on by abc.ABCMeta.__subclasscheck__().
    It should return True, False or NotImplemented.  If it returns
    NotImplemented, the normal algorithm is used.  Otherwise, it
    overrides the normal algorithm (and the outcome is cached).`

   
<span id="Map">class
**Map**</span>([collections.UserDict](collections.html#UserDict))

`   `

`Map(*args, **kwargs)    `

 

  - Method resolution order:  
    [Map](uxf.html#Map)
    [collections.UserDict](collections.html#UserDict)
    [collections.abc.MutableMapping](collections.abc.html#MutableMapping)
    [collections.abc.Mapping](collections.abc.html#Mapping)
    [collections.abc.Collection](collections.abc.html#Collection)
    [collections.abc.Sized](collections.abc.html#Sized)
    [collections.abc.Iterable](collections.abc.html#Iterable)
    [collections.abc.Container](collections.abc.html#Container)
    [builtins.object](builtins.html#object)

-----

Methods defined here:  

  - <span id="Map-__init__">**\_\_init\_\_**</span>(self, \*args,
    \*\*kwargs)  
    `Takes same arguments as dict. .data holds the actual dict
    .comment holds an optional comment
    .ktype and .vtype hold a UXF type name ('int', 'str', …);
    .ktype may only be int, str, bytes, date, or datetime`

<!-- end list -->

  - <span id="Map-append">**append**</span>(self, value)  
    `If there's no pending key, sets the value as the pending key;
    otherwise adds a new item with the pending key and this value and
    clears the pending key.`

-----

Data and other attributes defined here:  

**\_\_abstractmethods\_\_** = frozenset()

-----

Methods inherited from
[collections.UserDict](collections.html#UserDict):  

  - <span id="Map-__contains__">**\_\_contains\_\_**</span>(self, key)  
    `# Modify __contains__ to work correctly when __missing__ is present`

<span id="Map-__copy__">**\_\_copy\_\_**</span>(self)

<span id="Map-__delitem__">**\_\_delitem\_\_**</span>(self, key)

<span id="Map-__getitem__">**\_\_getitem\_\_**</span>(self, key)

<span id="Map-__iter__">**\_\_iter\_\_**</span>(self)

<span id="Map-__len__">**\_\_len\_\_**</span>(self)

  - <span id="Map-__repr__">**\_\_repr\_\_**</span>(self)  
    `Return repr(self).`

<span id="Map-__setitem__">**\_\_setitem\_\_**</span>(self, key, item)

<span id="Map-copy">**copy**</span>(self)

-----

Class methods inherited from
[collections.UserDict](collections.html#UserDict):  

<span id="Map-fromkeys">**fromkeys**</span>(iterable, value=None) from
[abc.ABCMeta](abc.html#ABCMeta)

-----

Data descriptors inherited from
[collections.UserDict](collections.html#UserDict):  

  - **\_\_dict\_\_**  
    `dictionary for instance variables (if defined)`

<!-- end list -->

  - **\_\_weakref\_\_**  
    `list of weak references to the object (if defined)`

-----

Methods inherited from
[collections.abc.MutableMapping](collections.abc.html#MutableMapping):  

  - <span id="Map-clear">**clear**</span>(self)  
    `D.clear() -> None.  Remove all items from D.`

<!-- end list -->

  - <span id="Map-pop">**pop**</span>(self, key, default=\<object object
    at 0x7f0c918b7150\>)  
    `D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
    If key is not found, d is returned if given, otherwise KeyError is raised.`

<!-- end list -->

  - <span id="Map-popitem">**popitem**</span>(self)  
    `D.popitem() -> (k, v), remove and return some (key, value) pair
    as a 2-tuple; but raise KeyError if D is empty.`

<!-- end list -->

  - <span id="Map-setdefault">**setdefault**</span>(self, key,
    default=None)  
    `D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D`

<!-- end list -->

  - <span id="Map-update">**update**</span>(self, other=(), /,
    \*\*kwds)  
    `D.update([E, ]**F) -> None.  Update D from mapping/iterable E and F.
    If E present and has a .keys() method, does:     for k in E: D[k] = E[k]
    If E present and lacks .keys() method, does:     for (k, v) in E: D[k] = v
    In either case, this is followed by: for k, v in F.items(): D[k] = v`

-----

Methods inherited from
[collections.abc.Mapping](collections.abc.html#Mapping):  

  - <span id="Map-__eq__">**\_\_eq\_\_**</span>(self, other)  
    `Return self==value.`

<!-- end list -->

  - <span id="Map-get">**get**</span>(self, key, default=None)  
    `D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.`

<!-- end list -->

  - <span id="Map-items">**items**</span>(self)  
    `D.items() -> a set-like object providing a view on D's items`

<!-- end list -->

  - <span id="Map-keys">**keys**</span>(self)  
    `D.keys() -> a set-like object providing a view on D's keys`

<!-- end list -->

  - <span id="Map-values">**values**</span>(self)  
    `D.values() -> an object providing a view on D's values`

-----

Data and other attributes inherited from
[collections.abc.Mapping](collections.abc.html#Mapping):  

**\_\_hash\_\_** = None

**\_\_reversed\_\_** = None

-----

Class methods inherited from
[collections.abc.Collection](collections.abc.html#Collection):  

  - <span id="Map-__subclasshook__">**\_\_subclasshook\_\_**</span>(C)
    from [abc.ABCMeta](abc.html#ABCMeta)  
    `Abstract classes can override this to customize issubclass().  
    This is invoked early on by abc.ABCMeta.__subclasscheck__().
    It should return True, False or NotImplemented.  If it returns
    NotImplemented, the normal algorithm is used.  Otherwise, it
    overrides the normal algorithm (and the outcome is cached).`

   
<span id="TClass">class
**TClass**</span>([builtins.object](builtins.html#object))

`   `

`TClass(ttype, fields=None, *, comment=None)    `

 

Methods defined here:  

<span id="TClass-__bool__">**\_\_bool\_\_**</span>(self)

  - <span id="TClass-__hash__">**\_\_hash\_\_**</span>(self)  
    `Return hash(self).`

<!-- end list -->

  - <span id="TClass-__init__">**\_\_init\_\_**</span>(self, ttype,
    fields=None, \*, comment=None)  
    `The type of a Table
    .ttype holds the tclass's name (equivalent to a vtype or ktype
    name); it may not be the same as a built-in type name or constant
    .fields holds a list of field names or of fields of type Field
    .comment holds an optional comment`

<span id="TClass-__len__">**\_\_len\_\_**</span>(self)

  - <span id="TClass-__lt__">**\_\_lt\_\_**</span>(self, other)  
    `Return self<value.`

<!-- end list -->

  - <span id="TClass-__repr__">**\_\_repr\_\_**</span>(self)  
    `Return repr(self).`

<span id="TClass-append">**append**</span>(self, name\_or\_field,
vtype=None)

<span id="TClass-set_vtype">**set\_vtype**</span>(self, index, vtype)

-----

Data descriptors defined here:  

  - **\_\_dict\_\_**  
    `dictionary for instance variables (if defined)`

<!-- end list -->

  - **\_\_weakref\_\_**  
    `list of weak references to the object (if defined)`

**ttype**

   
<span id="Table">class
**Table**</span>([builtins.object](builtins.html#object))

`   `

`Table(tclass=None, *, records=None, comment=None)  
Used to store a UXF table.  
A Table has a list of fields (name, optional type) and a records list
which is a list of lists of scalars. with each sublist having the same
number of items as the number of fields. It also has a .comment
attribute. (Note that the lists in a Table are plain lists not UXF
Lists.)  
The only type-safe way to add values to a table is via .append() for
single values or += for single values or a sequence of values.  
When a Table is iterated each row is returned as a namedtuple. `

 

Methods defined here:  

  - <span id="Table-__getitem__">**\_\_getitem\_\_**</span>(self, row)  
    `Return the row-th record as a namedtuple`

<span id="Table-__iadd__">**\_\_iadd\_\_**</span>(self, value)

  - <span id="Table-__init__">**\_\_init\_\_**</span>(self, tclass=None,
    \*, records=None, comment=None)  
    `A Table may be created empty, e.g., Table(). However, if records is
    not None, then the tclass (of type TClass) must be given.  
    .records can be a flat list of values (which will be put into a list
    of lists with each sublist being len(fields) long), or a list of
    lists in which case each list is _assumed_ to be len(fields) i.e.,
    len(tclass.fields), long
    .RecordClass is a dynamically created namedtuple that is used when
    accessing a single record via [] or when iterating a table's
    records.   comment is an optional str.  
    See also the table() convenience function.`

<span id="Table-__iter__">**\_\_iter\_\_**</span>(self)

<span id="Table-__len__">**\_\_len\_\_**</span>(self)

  - <span id="Table-__repr__">**\_\_repr\_\_**</span>(self)  
    `Return repr(self).`

<!-- end list -->

  - <span id="Table-__str__">**\_\_str\_\_**</span>(self)  
    `Return str(self).`

<!-- end list -->

  - <span id="Table-append">**append**</span>(self, value)  
    `Use to append a value to the table. The value will be added to
    the last row if that isn't full, or as the first value in a new
    row`

<span id="Table-field">**field**</span>(self, column)

-----

Readonly properties defined here:  

**fields**

**is\_scalar**

**ttype**

-----

Data descriptors defined here:  

  - **\_\_dict\_\_**  
    `dictionary for instance variables (if defined)`

<!-- end list -->

  - **\_\_weakref\_\_**  
    `list of weak references to the object (if defined)`

   
<span id="Uxf">class
**Uxf**</span>([builtins.object](builtins.html#object))

`   `

`Uxf(data=None, *, custom='', tclasses=None, comment=None)  
A Uxf object holds three attributes.  
.data is a List, Map, or Table of data
.custom is an opional custom string used for customizing the file format
.tclasses is a dict where each key is a ttype (i.e., the .tclass.ttype
which is a TClass's name) and each value is a TClass object.
.comment is an optional file-level comment `

 

Methods defined here:  

  - <span id="Uxf-__init__">**\_\_init\_\_**</span>(self, data=None, \*,
    custom='', tclasses=None, comment=None)  
    `data may be a list, List, tuple, dict, Map, or Table and will
    default to a List if not specified; if given tclasses must be a dict
    whose values are TClasses and whose corresponding keys are the
    TClasses' ttypes (i.e., their names); if given the comment is a
    file-level comment that follows the uxf header and precedes any
    TClasses and data`

<!-- end list -->

  - <span id="Uxf-dump">**dump**</span>(self, filename\_or\_filelike,
    \*, indent=2, use\_true\_false=False, on\_error=\<function on\_error
    at 0x7f0c914fb280\>)  
    `Convenience method that wraps the module-level dump() function`

<!-- end list -->

  - <span id="Uxf-dumps">**dumps**</span>(self, \*, indent=2,
    use\_true\_false=False, on\_error=\<function on\_error at
    0x7f0c914fb280\>)  
    `Convenience method that wraps the module-level dumps() function`

<!-- end list -->

  - <span id="Uxf-load">**load**</span>(self, filename\_or\_filelike,
    \*, on\_error=\<function on\_error at 0x7f0c914fb280\>)  
    `Convenience method that wraps the module-level load() function`

<!-- end list -->

  - <span id="Uxf-loads">**loads**</span>(self, uxt, filename='-', \*,
    on\_error=\<function on\_error at 0x7f0c914fb280\>)  
    `Convenience method that wraps the module-level loads() function`

-----

Readonly properties defined here:  

**import\_filenames**

-----

Data descriptors defined here:  

  - **\_\_dict\_\_**  
    `dictionary for instance variables (if defined)`

<!-- end list -->

  - **\_\_weakref\_\_**  
    `list of weak references to the object (if defined)`

**data**

   
**Functions**

`      `

 

  - <span id="-canonicalize">**canonicalize**</span>(name,
    is\_table\_name=True)  
    `Given a name, returns a name that is a valid table or field name.
    is_table_name must be True (the default) for tables since table names
    have additional constraints. (See uxfconvert.py for uses.)`

<!-- end list -->

  - <span id="-dump">**dump**</span>(filename\_or\_filelike, data, \*,
    indent=2, use\_true\_false=False, on\_error=\<function on\_error at
    0x7f0c914fb280\>)  
    `filename_or_filelike is sys.stdout or a filename or an open writable
    file (text mode UTF-8 encoded). If filename_or_filelike is a filename
    with a .gz suffix then the output will be gzip-compressed.  
    data is a Uxf object, or a list, List, dict, Map, or Table, that this
    function will write to the filename_or_filelike in UXF format.  
    Set indent to 0 (and use_true_false to True) to minimize the file size.
     
    If use_true_false is False (the default), bools are output as 'yes' or
    'no'; but if use_true_false is True the are output as 'true' or 'false'.`

<!-- end list -->

  - <span id="-dumps">**dumps**</span>(data, \*, indent=2,
    use\_true\_false=False, on\_error=\<function on\_error at
    0x7f0c914fb280\>)  
    `data is a Uxf object, or a list, List, dict, Map, or Table that this
    function will write to a string in UXF format which will then be
    returned.  
    Set indent to 0 (and use_true_false to True) to minimize the string's
    size.  
    If use_true_false is False (the default), bools are output as 'yes' or
    'no'; but if use_true_false is True the are output as 'true' or 'false'.`

<span id="-is_scalar">**is\_scalar**</span>(x)

  - <span id="-load">**load**</span>(filename\_or\_filelike, \*,
    on\_error=\<function on\_error at 0x7f0c914fb280\>,
    \_imported=None)  
    `Returns a Uxf object.  
    filename_or_filelike is sys.stdin or a filename or an open readable file
    (text mode UTF-8 encoded, optionally gzipped).`

<!-- end list -->

  - <span id="-loads">**loads**</span>(uxt, filename='-', \*,
    on\_error=\<function on\_error at 0x7f0c914fb280\>,
    \_imported=None)  
    `Returns a Uxf object.   uxt must be a string of UXF data.`

<!-- end list -->

  - <span id="-naturalize">**naturalize**</span>(s)  
    `Given string s returns True if the string is 't', 'true', 'y', 'yes',
    or False if the string is 'f', 'false', 'n', 'no' (case-insensitive), or
    an int if s holds a parsable int, or a float if s holds a parsable
    float, or a datetime.datetime if s holds a parsable ISO8601 datetime
    string, or a datetime.date if s holds a parsable ISO8601 date string, or
    failing these returns the string s unchanged.`

   
**Data**

`      `

 

**VERSION** = 1.0  
**\_\_all\_\_** = ('\_\_version\_\_', 'VERSION', 'load', 'loads',
'dump', 'dumps', 'naturalize', 'canonicalize', 'is\_scalar', 'Uxf',
'List', 'Map', 'Table', 'TClass', 'Field')
