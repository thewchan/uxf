// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

use crate::value::Value;

#[derive(Debug)]
pub struct List {
    vtype: Option<String>,
    comment: Option<String>,
    data: Vec<Option<Value>>,
}
