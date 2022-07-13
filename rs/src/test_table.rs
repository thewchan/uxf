// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

#[cfg(test)]
mod tests {
    use crate::table::Table;
    use crate::tclass::TClass;
    use crate::test_utils::value_to_str;
    use crate::value::Value;

    #[test]
    fn test_table() {
        let tclass = TClass::new("Point");
        let t = Table::new(tclass);
        let v = Value::Table(t);
        assert_eq!(
            value_to_str(v),
            "Table { tclass: TClass { ttype: \"Point\", comment: \
                   None, fields: [] }, comment: None, records: [] }"
        );
        assert!(false, "TODO test_table"); // TODO
    }
}
