// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

use crate::tclass::TClass;
use crate::value::Value;

#[derive(Clone, Debug)]
pub struct Table {
    tclass: TClass,
    comment: Option<String>,
    records: Vec<Vec<Option<Value>>>,
}

impl Table {
    pub fn new(tclass: TClass) -> Self {
        Table { tclass, comment: None, records: vec![] }
    }
}
