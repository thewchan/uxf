// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

#[cfg(test)]
mod tests {
    use crate::constants::*;
    use crate::field::Field;

    #[test]
    fn field_new_valid_name_valid_vtype() {
        for (i, vtype) in [
            VTYPE_NAME_BOOL,
            VTYPE_NAME_BYTES,
            VTYPE_NAME_DATE,
            VTYPE_NAME_DATETIME,
            VTYPE_NAME_INT,
            VTYPE_NAME_LIST,
            VTYPE_NAME_MAP,
            VTYPE_NAME_REAL,
            VTYPE_NAME_STR,
            VTYPE_NAME_TABLE,
            "MyType",
            "Custom_",
            "_special",
            "_99",
            "a_y_47ĕặæ_",
        ]
        .iter()
        .enumerate()
        {
            let name = format!("{}{}", vtype, i + 1);
            let h = Field::new(&name, Some(vtype)).unwrap();
            assert_eq!(
                h.to_string(),
                format!("Field::new({:?}, Some({:?}))", name, vtype)
            );
            assert_eq!(h.name(), name);
            assert_eq!(&h.vtype().unwrap(), vtype);
        }
    }

    #[test]
    fn field_new_invalid_name() {
        for (code, name) in [
            (304, VALUE_NAME_NULL),
            (304, VTYPE_NAME_BOOL),
            (304, VTYPE_NAME_BYTES),
            (304, VTYPE_NAME_DATE),
            (304, VTYPE_NAME_DATETIME),
            (304, VTYPE_NAME_INT),
            (304, VTYPE_NAME_LIST),
            (304, VTYPE_NAME_MAP),
            (304, VTYPE_NAME_REAL),
            (304, VTYPE_NAME_STR),
            (304, VTYPE_NAME_TABLE),
            (602, "*abc"),
            (602, "1int"),
            (602, "€200"),
            (604, BOOL_FALSE),
            (604, BOOL_TRUE),
            (
                606,
                "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\
                   xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxy",
            ),
            (608, "e—"),
            (608, "_almost#1"),
            (608, "f1:"),
        ] {
            let g = Field::new(name, None);
            assert!(g.is_err(), "expected err of #{} on {}", code, name);
            let e = g.unwrap_err();
            check_error_code(&e.to_string(), code, name);
        }
    }

    #[test]
    fn field_new_invalid_vtype() {
        for (code, vtype) in [
            (600, ""),
            (602, "*abc"),
            (602, ".Custom_"),
            (602, "1int"),
            (602, "€200"),
            (604, BOOL_FALSE),
            (604, BOOL_TRUE),
            (
                606,
                "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\
                   xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxy",
            ),
            (608, "My.Type"),
            (608, "_9.9"),
            (608, "_almost#1"),
            (608, "_special."),
            (608, "a_y_47ĕặæ_."),
            (608, "e—"),
            (608, "f1:"),
        ] {
            let g = Field::new("test", Some(vtype));
            assert!(g.is_err(), "expected err of #{} on {}", code, vtype);
            let e = g.unwrap_err();
            check_error_code(&e.to_string(), code, vtype);
        }
    }

    #[test]
    fn field_name() {
        assert!(false, "TODO get/set field name with valid & invalid");
    }

    #[test]
    fn field_vtype() {
        assert!(false, "TODO get/set field vtype with valid & invalid");
    }

    fn check_error_code(error: &str, code: i32, name: &str) {
        match code {
            600 => assert_eq!(error, "#600:type names must be nonempty"),
            602 => assert_eq!(
                error,
                format!(
                    "#602:type names must start \
                                  with a letter or underscore, got {}",
                    name
                )
            ),
            604 => assert_eq!(
                error,
                format!(
                    "#604:type names may not be yes or no got {}",
                    name
                )
            ),
            606 => {
                let n = name.len(); // byte count is fine: all ASCII
                assert_eq!(
                    error,
                    format!(
                        "#606:type names may be at most \
                               {} characters long, got {} ({} characters)",
                        MAX_IDENTIFIER_LEN, name, n
                    )
                );
            }
            608 => assert_eq!(
                error,
                format!(
                    "#608:type names may only \
                                  contain letters, digits, or \
                                  underscores, got {}",
                    name
                )
            ),
            _ => {
                assert_eq!(code, 304, "code={} name={}", code, name);
                assert_eq!(
                    error,
                    format!(
                        "#304:names cannot be the same \
                               as built-in type names or constants, got {}",
                        name
                    )
                );
            }
        }
    }
}
