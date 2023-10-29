// use crate::database::driver::DatabaseDriver;

use config::configuration::Config;
use validator::Validate;

use crate::database::sqlite;

pub mod cli;
pub mod config;
pub mod database;
pub mod f2b;
pub mod logging;

/// Public interface for initializing logging.
fn init_logging(logging_environment: String) {
    logging::set_logging_environment(logging_environment);
    env_logger::init();
    log::info!("Starting fail2ban-monitoring");
}

fn parse_configuration() -> Config {
    log::info!("Reading configuration file");
    config::configuration::Config::new().read_configuration()
}

pub async fn start_procedure(logging_environment: String) {
    init_logging(logging_environment);
    let config = parse_configuration();
    log::debug!("Configuration: {:?}", config);
    match config.validate() {
        Ok(_) => {
            log::info!("Configuration is valid");
        }
        Err(e) => {
            log::error!("Configuration is invalid: {}", e);
            std::process::exit(1);
        }
    }
    println!("Configuration: {:?}", config);
    sqlite::SqliteDriver::new(config).initialize().await;
}
