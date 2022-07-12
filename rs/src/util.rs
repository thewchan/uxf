// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

use anyhow::{bail, Result};
use crate::constants::*;

pub(crate) fn check_name(name: &str) -> Result<()> {
    check_type_name(name)?;
    if is_reserved_name(name) {
        bail!("#304:names cannot be the same as built-in type names or \
              constants, got {}", name);
    }
    Ok(())
}

pub(crate) fn check_type_name(name: &str) -> Result<()> {
    if name.is_empty() {
        bail!("#600:type names must be nonempty");
    }
    let first = name.chars().next().unwrap(); // safe because nonempty
    if !(first == '_' || first.is_alphabetic()) {
        bail!("#602:type names must start with a letter or underscore, \
              got {}", name);
    }
    for (i, c) in name.chars().enumerate() {
        if i == MAX_IDENTIFIER_LEN {
            bail!("#604:type names may be at most {} characters long, \
                  got {} ({} characters)", i, name, i);
        }
        if !(c == '_' || c.is_alphanumeric()) {
            bail!("#606:type names may only contain letters, digits, or \
                  underscores, got {}", name);
        }
    }
    Ok(())
}

pub fn is_ktype_name(ktype: &str) -> bool {
   [VALUE_NAME_BYTES, VALUE_NAME_DATE, VALUE_NAME_INT, VALUE_NAME_STR]
        .contains(&ktype)
}

pub fn is_reserved_name(name: &str) -> bool {
    [VALUE_NAME_NULL, VALUE_NAME_BOOL, VALUE_NAME_BYTES, VALUE_NAME_DATE,
     VALUE_NAME_DATETIME, VALUE_NAME_INT, VALUE_NAME_LIST, VALUE_NAME_MAP,
     VALUE_NAME_REAL, VALUE_NAME_STR, VALUE_NAME_TABLE,
     BOOL_FALSE, BOOL_TRUE].contains(&name)
}
