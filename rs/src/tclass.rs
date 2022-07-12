// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

use crate::value::Value;
use std::fmt;

#[derive(Debug)]
pub struct TClass {
    ttype: String,
    comment: Option<String>,
    fields: Vec<Field>,
}

impl TClass {
    pub fn new(ttype: &str, comment: Option<&str>) -> Self {
        TClass {
            ttype: ttype.to_string(),
            comment: comment.map(|s| s.to_string()),
            fields: vec![],
        }
    }
}

#[derive(Debug)]
pub struct Field {
    name: String,
    vtype: Option<String>,
}
