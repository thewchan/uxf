// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

use crate::constants::*;
use crate::value::Value;
use anyhow::{bail, Result};

#[cfg(test)]
pub fn opt_value_to_str(v: Option<Value>) -> String {
    match v {
        None => "?".to_string(),
        Some(v) => value_to_str(v),
    }
}

#[cfg(test)]
pub fn value_to_str(v: Value) -> String {
    match v {
        // TODO better output for List, Map, Table
        Value::Bool(true) => "yes".to_string(),
        Value::Bool(false) => "no".to_string(),
        Value::Bytes(b) => format!("{:?}", b),
        Value::Date(d) => d.format(ISO8601_DATE).to_string(),
        Value::DateTime(dt) => dt.format(ISO8601_DATETIME).to_string(),
        Value::Int(i) => format!("{}", i),
        Value::List(lst) => format!("{:?}", lst),
        Value::Map(m) => format!("{:?}", m),
        Value::Real(r) => format!("{}", r),
        Value::Str(s) => s,
        Value::Table(t) => format!("{:?}", t),
    }
}
