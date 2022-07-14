// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

#[cfg(test)]
mod tests {
    use crate::table::Table;
    use crate::tclass::TClass;
    use crate::test_utils::value_to_str;
    use crate::value::Value;

    #[test]
    fn t_table() {
        let tclass = TClass::new_fieldless("Point", None).unwrap();
        let t = Table::new(tclass);
        let v = Value::Table(t);
        assert_eq!(
            value_to_str(v),
            "Table { tclass: TClass { ttype: \"Point\", fields: [], \
            comment: None }, comment: None, records: [] }"
        );
        // TODO lots more tests
    }
}
