// use crate::database::driver::DatabaseDriver;

use config::configuration::Config;

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

pub fn start_procedure(logging_environment: String) {
    init_logging(logging_environment);
    let config = parse_configuration();
    log::debug!("Configuration: {:?}", config);
}
