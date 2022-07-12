// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

#[cfg(test)]
mod tests {
    use crate::table::Table;
    use crate::tclass::TClass;
    use crate::value::{Value, ISO8601_DATE, ISO8601_DATETIME};

    #[test]
    fn single_values() {
        let n = None;
        assert_eq!(opt_value_to_str(n), "?");
        let b = Some(Value::Bool(true));
        assert_eq!(opt_value_to_str(b), "yes");
        let b = Value::Bool(false);
        assert_eq!(value_to_str(b), "no");
        let i = Value::Int(987123);
        assert_eq!(value_to_str(i), "987123");
    }

    #[test]
    fn list_values() {
        // TODO
    }

    #[test]
    fn map_values() {
        // TODO
    }

    #[test]
    fn table_values() {
        // TODO
        let tclass = TClass::new("Point");
        let t = Table::new(tclass);
        let v = Value::Table(t);
        assert_eq!(
            value_to_str(v),
            "Table { tclass: TClass { ttype: \"Point\", comment: \
                   None, fields: [] }, comment: None, records: [] }"
        );
    }

    fn opt_value_to_str(v: Option<Value>) -> String {
        match v {
            None => "?".to_string(),
            Some(v) => value_to_str(v),
        }
    }

    fn value_to_str(v: Value) -> String {
        match v {
            // TODO better output for List, Map, Table
            Value::Bool(true) => "yes".to_string(),
            Value::Bool(false) => "no".to_string(),
            Value::Bytes(b) => format!("{:?}", b),
            Value::Date(d) => d.format(ISO8601_DATE).to_string(),
            Value::DateTime(dt) => dt.format(ISO8601_DATETIME).to_string(),
            Value::Int(i) => format!("{}", i),
            Value::List(lst) => format!("{:?}", lst),
            Value::Map(m) => format!("{:?}", m),
            Value::Real(r) => format!("{}", r),
            Value::Str(s) => s,
            Value::Table(t) => format!("{:?}", t),
        }
    }
}
