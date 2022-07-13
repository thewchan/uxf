// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

#[cfg(test)]
mod tests {
    use crate::constants::*;
    use crate::field::Field;

    #[test]
    fn field_type() {
        // Valid name; no vtype
        let f = Field::new("any", None).unwrap();
        assert_eq!(f.to_string(), "Field::new(\"any\", None)");
        assert_eq!(f.name(), "any");
        assert_eq!(f.vtype(), None);
        // Invalid name no vtype
        for (code, name) in [
            (304, VALUE_NAME_NULL),
            (304, VALUE_NAME_BOOL),
            (304, VALUE_NAME_BYTES),
            (304, VALUE_NAME_DATE),
            (304, VALUE_NAME_DATETIME),
            (304, VALUE_NAME_INT),
            (304, VALUE_NAME_LIST),
            (304, VALUE_NAME_MAP),
            (304, VALUE_NAME_REAL),
            (304, VALUE_NAME_STR),
            (304, VALUE_NAME_TABLE),
            (600, ""),
            (602, "1int"),
            (604,
             "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"),
            (606, "f1:"),
        ] {
            let g = Field::new(name, None);
            assert!(g.is_err());
            let e = g.unwrap_err();
            match code {
                600 => assert_eq!(e.to_string(),
                                  "#600:type names must be nonempty"),
                602 => assert_eq!(e.to_string(),
                                  format!("#602:type names must start \
                                  with a letter or underscore, got {}",
                                  name)),
                604 => {
                    let n = name.len(); // byte count is fine: all ASCII
                    assert_eq!(e.to_string(),
                               format!("#604:type names may be at most \
                               {} characters long, got {} ({} characters)",
                               n, name, n));
                }
                606 => assert_eq!(e.to_string(),
                                  format!("#606:type names may only \
                                  contain letters, digits, or \
                                  underscores, got {}", name)),
                _ => {
                    assert_eq!(code, 304);
                    assert_eq!(e.to_string(),
                               format!("#304:names cannot be the same \
                               as built-in type names or constants, got ",
                               name));
                }
            }
        }
        // Valid name and valid vtype
        for (i, vtype) in [
            VALUE_NAME_BOOL,
            VALUE_NAME_BYTES,
            VALUE_NAME_DATE,
            VALUE_NAME_DATETIME,
            VALUE_NAME_INT,
            VALUE_NAME_LIST,
            VALUE_NAME_MAP,
            VALUE_NAME_REAL,
            VALUE_NAME_STR,
            VALUE_NAME_TABLE,
            "MyType",
            "Custom_",
            "_special",
        ]
        .iter()
        .enumerate()
        {
            let name = format!("{}{}", vtype, i + 1);
            let h = Field::new(&name, Some(vtype)).unwrap();
            assert_eq!(
                h.to_string(),
                format!("Field::new({:?}, {:?})", name, vtype)
            );
            assert_eq!(h.name(), name);
            assert_eq!(&h.vtype().unwrap(), vtype);
        }
        // TODO
        // Valid name and invalid vtype
    }
}
