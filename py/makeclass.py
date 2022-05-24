#!/usr/bin/env python3

def make_class(classname, *fieldnames):
    fields = {name: None for name in fieldnames}
    def init(self, *args):
        for name, value in zip(fieldnames, args):
            setattr(self, name, value)
    def repr(self):
        values = []
        for name in fieldnames:
            values.append(getattr(self, name))
        values = ', '.join(f'{value!r}' for value in values)
        return f'{classname}({values})'
    def getitem(self, index):
        if index >= len(fieldnames):
            raise IndexError(
                f'{classname}: no item to get at index {index}')
        return getattr(self, fieldnames[index])
    def setitem(self, index, value):
        if index >= len(fieldnames):
            raise IndexError(
                f'{classname}: no item to set at index {index}')
        setattr(self, fieldnames[index], value)
    Row = type(classname, (), dict(__init__=init, __repr__=repr,
        __getitem__=getitem, __setitem__=setitem, **fields))
    return Row


fieldnames = ('width', 'height')
Row = make_class('Row', *fieldnames)

r = Row(-7, 29)
print(r, r.width, r.height)
print(r, r[0], r[1])
r.width *= -2
r[1] -= 3
print(r, r.width, r.height)
print(r, r[0], r[1])
try:
    print(r[2])
    print('FAIL')
except IndexError as err:
    print(f'expected {err}')
try:
    print(r.missing)
    print('FAIL')
except AttributeError as err:
    print(f'expected {err}')
