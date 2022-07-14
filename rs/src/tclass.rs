// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

use crate::field::Field;
use crate::util;
use crate::value::Value;
use anyhow::{bail, Result};
use std::fmt;

#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TClass {
    ttype: String,
    fields: Vec<Field>,
    comment: Option<String>,
}

impl TClass {
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

    pub fn fieldless(&self) -> bool {
        self.fields.len() == 0
    }

    pub fn ttype(&self) -> &str {
        &self.ttype
    }

    pub fn comment(&self) -> Option<&str> {
        match &self.comment {
            None => None,
            Some(comment) => Some(comment),
        }
    }

    pub fn len(&self) -> usize {
        self.fields.len()
    }

    pub fn record_of_nulls(&self) -> Result<Vec<Option<Value>>> {
        if self.fieldless() {
            bail!("#352:can't create a record of nulls for a fieldless \
                  table's tclass");
        }
        let mut record = Vec::with_capacity(self.len());
        record.fill(None);
        Ok(record)
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
