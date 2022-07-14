// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

use crate::util;
use anyhow::Result;
use std::{cmp::Ordering, fmt};

/// Provides a definition of a field (`name` and `vtype`) for use in
/// ``TClass``es.
///
/// ``Field``s are immutable.
#[derive(Clone, Debug, Eq)]
pub struct Field {
    name: String,
    vtype: Option<String>,
}

impl Field {
    /// Creates a new `Field` with the given `name` and `vtype` _or_
    /// returns an Err if either or both is or are invalid.
    pub fn new(name: &str, vtype: &str) -> Result<Self> {
        util::check_name(name)?;
        util::check_type_name(vtype)?;
        Ok(Field { name: name.to_string(), vtype: Some(vtype.to_string()) })
    }

    /// Creates a new `Field` with the given `name` and a `vtype` of `None`
    /// _or_ returns an Err if `name` is invalid.
    ///
    /// A `vtype` of `None` signifies that this `Field` will accept a value
    /// of _any_ `Value` type.
    pub fn new_anyvtype(name: &str) -> Result<Self> {
        util::check_name(name)?;
        Ok(Field { name: name.to_string(), vtype: None })
    }

    /// Return's the ``Field``'s `name`.
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Return's the ``Field``'s `vtype` (which may be `None`).
    pub fn vtype(&self) -> Option<&str> {
        match &self.vtype {
            None => None,
            Some(vtype) => Some(vtype),
        }
    }
}

impl Ord for Field {
    fn cmp(&self, other: &Self) -> Ordering {
        let aname = self.name.to_uppercase();
        let bname = other.name.to_uppercase();
        if aname != bname { // prefer case-insensitive ordering
            aname.cmp(&bname)
        } else if self.name != other.name {
            self.name.cmp(&other.name)
        } else { // identical names names so use vtype to tie-break
            self.vtype.cmp(&other.vtype)
        }
    }
}

impl PartialOrd for Field {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl PartialEq for Field {
    fn eq(&self, other: &Self) -> bool {
        self.name == other.name && self.vtype == other.vtype
    }
}

impl fmt::Display for Field {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match &self.vtype {
            Some(vtype) => {
                write!(f, "Field::new({:?}, {:?})", self.name, vtype)
            }
            None => write!(f, "Field::new_anyvtype({:?})", self.name),
        }
    }
}
