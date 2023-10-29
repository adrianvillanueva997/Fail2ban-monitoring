use std::{
    net::{Ipv4Addr, Ipv6Addr},
    path::Path,
};

use serde::Deserialize;
use validator::{Validate, ValidationError};

#[derive(Debug, Validate, Deserialize, Default, Clone)]
pub struct Config {
    #[validate(custom = "check_driver")]
    pub driver: String,
    pub username: String,
    pub password: String,
    #[validate(custom = "check_host")]
    pub host: String,
    #[validate(range(min = 1, max = 65535))]
    pub port: i16,
    pub database: String,
}

// TODO: Write documentation for these functions.
impl Config {
    pub fn new() -> Self {
        Self::default()
    }

    fn configuration_file_exists(&self) -> bool {
        //TODO: Maybe let the user specify a custom config file path?
        Path::new("config.yml").is_file()
    }

    pub fn read_configuration(&mut self) -> Self {
        if self.configuration_file_exists() {
            log::info!("Configuration file found");
            let config_file = std::fs::read_to_string("config.yml").unwrap();
            let config: Config = serde_yaml::from_str(&config_file).unwrap();
            let validation = config.validate();
            match validation {
                Ok(_) => {
                    log::info!("Configuration file is valid");
                    self.database = config.database;
                    self.driver = config.driver;
                    self.host = config.host;
                    self.password = config.password;
                    self.port = config.port;
                    self.username = config.username;
                    self.clone()
                }
                Err(e) => {
                    log::error!("Configuration file is invalid: {}", e);
                    panic!("Configuration file is invalid")
                }
            }
        } else {
            log::error!("Configuration file not found");
            panic!("Configuration file not found")
        }
    }
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
