// Copyright © 2022 Mark Summerfield. All rights reserved.
// License: GPLv3

#[cfg(test)]
mod tests {
    use crate::test_utils::{opt_value_to_str, value_to_str};
    use crate::value::Value;

    #[test]
    fn t_single_value() {
        let n = None;
        assert_eq!(opt_value_to_str(n), "?");
        let b = Some(Value::Bool(true));
        assert_eq!(opt_value_to_str(b), "yes");
        let b = Value::Bool(false);
        assert_eq!(value_to_str(b), "no");
        let i = Value::Int(987123);
        assert_eq!(value_to_str(i), "987123");
        // TODO lots more tests
    }
}
