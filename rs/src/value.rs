// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

use crate::list::List;
use crate::map::Map;
use crate::table::Table;
use chrono::prelude::*;

// See also Michael-F-Bryan's replies in
// https://users.rust-lang.org/t/how-do-i-create-an-enum-that-subsumes-others/78232/8?u=mark

pub static ISO8601_DATE: &str = "%Y-%m-%d";
pub static ISO8601_DATETIME: &str = "%Y-%m-%dT%H:%M:%S";

#[derive(Debug)]
pub enum Value {
    Null,
    Bool(bool),
    Bytes(Vec<u8>),
    Date(NaiveDate),
    DateTime(NaiveDateTime),
    Int(i64),
    List(List),
    Map(Map),
    Real(f64),
    Str(String),
    Table(Table),
}

impl From<Scalar> for Value {
    fn from(scalar: Scalar) -> Self {
        match scalar {
            Scalar::Null => Value::Null,
            Scalar::Bool(b) => Value::Bool(b),
            Scalar::DateTime(dt) => Value::DateTime(dt),
            Scalar::Real(r) => Value::Real(r),
        }
    }
}

impl From<Key> for Value {
    fn from(key: Key) -> Self {
        match key {
            Key::Bytes(b) => Value::Bytes(b),
            Key::Date(d) => Value::Date(d),
            Key::Int(i) => Value::Int(i),
            Key::Str(s) => Value::Str(s),
        }
    }
}

impl From<Collection> for Value {
    fn from(collection: Collection) -> Self {
        match collection {
            Collection::List(lst) => Value::List(lst),
            Collection::Map(m) => Value::Map(m),
            Collection::Table(t) => Value::Table(t),
        }
    }
}

#[derive(Debug)]
pub enum Scalar {
    Null,
    Bool(bool),
    DateTime(NaiveDateTime),
    Real(f64),
}

#[derive(Debug)]
pub enum Key {
    Bytes(Vec<u8>),
    Date(NaiveDate),
    Int(i64),
    Str(String),
}

#[derive(Debug)]
pub enum Collection {
    List(List),
    Map(Map),
    Table(Table),
}
