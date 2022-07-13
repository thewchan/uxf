// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

/*!

uxf is a library that supports the UXF format. UXF is a plain text human
readable optionally typed storage format. UXF may serve as a convenient
alternative to csv, ini, json, sqlite, toml, xml, or yaml.

TODO

*/

mod constants;
mod field;
mod list;
mod map;
mod parser;
mod table;
mod tclass;
mod util;
mod value;

#[cfg(test)]
mod test_field;
#[cfg(test)]
mod test_list;
#[cfg(test)]
mod test_map;
#[cfg(test)]
mod test_table;
#[cfg(test)]
mod test_tclass;
#[cfg(test)]
mod test_utils;
#[cfg(test)]
mod test_value;

pub use crate::value::Value;
// pub use crate::parser::parser; // etc
