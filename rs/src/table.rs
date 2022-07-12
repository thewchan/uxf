// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

use crate::tclass::TClass;
use crate::value::Value;
use std::fmt;

pub struct Table {
    tclass: TClass,
    comment: Option<String>,
    records: Vec<Value>,
}

impl Table {
    pub fn new(tclass: TClass) -> Self {
        Table { tclass, comment: None, records: vec![] }
    }
}

impl fmt::Debug for Table {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("Table")
            .field("tclass", &self.tclass)
            .field("comment", &self.comment)
            .field("records", &self.records)
            .finish()
    }
}
