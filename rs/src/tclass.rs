// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

use crate::field::Field;
use crate::util;
use anyhow::Result;

#[derive(Debug)]
pub struct TClass {
    ttype: String,
    comment: Option<String>,
    fields: Vec<Field>,
}

impl TClass {
    pub fn new(ttype: &str) -> Self {
        TClass { ttype: ttype.to_string(), comment: None, fields: vec![] }
    }
}
