use std::net::{Ipv4Addr, Ipv6Addr};

use serde::Deserialize;
use validator::{Validate, ValidationError};

#[derive(Debug, Validate, Deserialize)]
pub struct Config {
    #[validate(custom = "check_driver")]
    pub driver: String,
    pub username: String,
    pub password: String,
    #[validate(custom = "check_host")]
    pub host: String,
    #[validate(range(min = 1, max = 65535))]
    pub port: u16,
    pub database: String,
}

/// Checks if the host is valid.
///
/// # Errors
///
/// This function will return an error if the host is not valid.
fn check_host(host: &str) -> Result<(), ValidationError> {
    match host {
        "localhost" => Ok(()),
        _ => {
            if let Ok(_ipv4) = host.parse::<Ipv4Addr>() {
                return Ok(());
            }
            if let Ok(__ipv6) = host.parse::<Ipv6Addr>() {
                return Ok(());
            }
            Err(ValidationError::new("host"))
        }
    }
}

/// Checks if the driver is valid. Valid drivers are mysql, postgres, and sqlite.
///
/// # Errors
///
/// This function will return an error if the driver is not valid.
fn check_driver(driver: &str) -> Result<(), ValidationError> {
    match driver {
        "mysql" => Ok(()),
        "postgres" => Ok(()),
        "sqlite" => Ok(()),
        _ => Err(ValidationError::new("driver")),
    }
}
