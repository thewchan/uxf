// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

use crate::field::Field;
use crate::util;
use crate::value::Value;
use anyhow::{bail, Result};
use std::fmt;
use std::fmt::Write as _;

/// Provides a definition of a tclass (`name`, `fields`, and `comment`)
/// for use in ``Table``s.
///
/// ``TClass``es are immutable.
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TClass {
    ttype: String,
    fields: Vec<Field>,
    comment: Option<String>,
}

impl TClass {
    /// Creates a new `TClass` with the given `name`, `fields`, and
    /// `commment` _or_ returns an Err if the `name` is invalid.
    pub fn new(
        ttype: &str,
        fields: Vec<Field>,
        comment: Option<&str>,
    ) -> Result<Self> {
        util::check_name(ttype)?;
        Ok(TClass {
            ttype: ttype.to_string(),
            comment: comment.map(|s| s.to_string()),
            fields,
        })
    }

    /// Creates a new `TClass` with the given `name`, no `fields`, and
    /// `commment` _or_ returns an Err if the `name` is invalid.
    pub fn new_fieldless(
        ttype: &str,
        comment: Option<&str>,
    ) -> Result<Self> {
        util::check_name(ttype)?;
        Ok(TClass {
            ttype: ttype.to_string(),
            comment: comment.map(|s| s.to_string()),
            fields: vec![],
        })
    }

    /// Returns true if this is a fieldless TClass; otherwise returns false.
    pub fn is_fieldless(&self) -> bool {
        self.fields.is_empty()
    }

    /// Returns this ``TClass``'s `ttype`.
    pub fn ttype(&self) -> &str {
        &self.ttype
    }

    /// Returns this ``TClass``'s `comment`.
    pub fn comment(&self) -> Option<&str> {
        match &self.comment {
            None => None,
            Some(comment) => Some(comment),
        }
    }

    /// Returns how many fields this ``TClass`` has; this will be `0` for a
    /// fieldless `TClass`.
    pub fn len(&self) -> usize {
        self.fields.len()
    }

    /// Returns a record with `TClass.len()` (i.e., `fields.len()`) fields,
    /// each holding an `Option<Value>` whose value is `None`.
    /// This is a helper for adding new rows to ``Table``s.
    pub fn record_of_nulls(&self) -> Result<Vec<Option<Value>>> {
        if self.is_fieldless() {
            bail!(
                "#352:can't create a record of nulls for a fieldless \
                  table's tclass"
            );
        }
        let mut record = Vec::with_capacity(self.len());
        record.fill(None);
        Ok(record)
    }
}

impl fmt::Display for TClass {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let mut s = String::from("TClass::");
        if self.is_fieldless() {
            s.push_str("new_fieldless(");
            let _ = write!(s, "{:?}, ", self.ttype);
        } else {
            s.push_str("new(");
            let _ = write!(s, "{:?}, vec![", self.ttype);
            let mut sep = "";
            for field in &self.fields {
                s.push_str(sep);
                s.push_str(&field.to_string());
                sep = ", ";
            }
            s.push_str("], ");
        }
        s.push_str(&match &self.comment {
            Some(comment) => format!("Some({:?})", comment),
            None => "None".to_string(),
        });
        s.push(')');
        write!(f, "{}", s)
    }
}
