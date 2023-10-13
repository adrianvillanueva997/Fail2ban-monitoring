// use crate::database::driver::DatabaseDriver;

pub mod cli;
pub mod config;
pub mod database;
pub mod f2b;
pub mod logging;

/// Public interface for initializing logging.
pub fn init_logging(logging_environment: String) {
    logging::set_logging_environment(logging_environment);
    env_logger::init();
    log::info!("Starting fail2ban-monitoring");
}
