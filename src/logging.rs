use std::env::set_var;

/// Sets the logging environment variable.
pub fn set_logging_environment(logging_environment: String) {
    set_var("RUST_LOG", logging_environment);
}
