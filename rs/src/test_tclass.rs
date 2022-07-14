// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

#[cfg(test)]
mod tests {
    use crate::constants::*;
    use crate::field::Field;
    use crate::tclass::TClass;
    use crate::test_utils::check_error_code;

    // TODO new() new_fieldless() is_fieldless() ttype() comment() len()
    // record_of_nulls() == != < clone()
    #[test]
    fn t_tclass() {
        // TODO with & without comment
    }

    #[test]
    fn t_tclass_display() {
        let fields = valid_fields();
        let tclass =
            TClass::new("General", fields, Some("first test")).unwrap();
        assert_eq!(
            tclass.to_string(),
            "TClass::new(\"General\", vec![Field::new(\"CID\", \"int\"), \
            Field::new(\"title\", \"str\"), \
            Field::new(\"selected\", \"bool\"), \
            Field::new(\"when\", \"date\"), \
            Field::new(\"size\", \"real\"), \
            Field::new(\"timestamp\", \"datetime\"), \
            Field::new_anyvtype(\"Kind\"), \
            Field::new_anyvtype(\"Filename\"), \
            Field::new(\"Categories\", \"Categories\"), \
            Field::new(\"Extra\", \"Point\")], Some(\"first test\"))"
        );
        let tclass =
            TClass::new_fieldless("StateReady", Some("enum")).unwrap();
        assert_eq!(
            tclass.to_string(),
            "TClass::new_fieldless(\"StateReady\", Some(\"enum\"))"
        );
    }

    #[test]
    fn t_tclass_new_fieldless() {
        // TODO with & without comment
    }

    #[test]
    fn t_tclass_invalid_ttype() {
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
            // With fields
            let fields = valid_fields();
            let tclass = TClass::new(name, fields, None);
            assert!(
                tclass.is_err(),
                "expected err of #{} on {}",
                code,
                name
            );
            let e = tclass.unwrap_err();
            check_error_code(&e.to_string(), code, name);
            // Fieldless
            let tclass = TClass::new_fieldless(name, None);
            assert!(
                tclass.is_err(),
                "expected err of #{} on {}",
                code,
                name
            );
            let e = tclass.unwrap_err();
            check_error_code(&e.to_string(), code, name);
        }
    }

    fn valid_fields() -> Vec<Field> {
        let mut fields = vec![];
        for (name, vtype) in [
            ("CID", "int"),
            ("title", "str"),
            ("selected", "bool"),
            ("when", "date"),
            ("size", "real"),
            ("timestamp", "datetime"),
            ("Kind", ""),
            ("Filename", ""),
            ("Categories", "Categories"),
            ("Extra", "Point"),
        ] {
            if vtype.is_empty() {
                fields.push(Field::new_anyvtype(name).unwrap());
            } else {
                fields.push(Field::new(name, vtype).unwrap());
            }
        }
        fields
    }
}
