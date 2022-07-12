// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

use crate::util;
use anyhow::Result;

#[derive(Debug)]
pub struct Field {
    name: String,
    vtype: Option<String>,
}

impl Field {
    pub fn maybe_new(name: &str, vtype: Option<&str>) -> Result<Self> {
        util::check_name(name)?;
        Ok(Field {
            name: name.to_string(),
            vtype: vtype.map(|s| s.to_string()),
        })
    }

    pub fn name(&self) -> &str {
        &self.name
    }

    pub fn set_name(&mut self, name: &str) -> Result<()> {
        util::check_name(name)?;
        self.name = name.to_string();
        Ok(())
    }

    pub fn vtype(&self) -> Option<&str> {
        match &self.vtype {
            None => None,
            Some(vtype) => Some(vtype),
        }
    }

    pub fn set_vtype(&mut self, vtype: &str) -> Result<()> {
        util::check_type_name(vtype)?;
        self.vtype = Some(vtype.to_string());
        Ok(())
    }
}
