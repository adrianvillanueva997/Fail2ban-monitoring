use clap::Parser;

pub mod f2b;
pub mod logging;
#[derive(Parser, Debug)]
#[command(
    name = "fail2ban-monitoring",
    version = "0.1.0",
    about = "fail2ban monitoring",
    long_about = None
)]
pub struct Args {
    #[arg(short, long, default_value = "info")]
    pub logging_environment: String,

    #[arg(short, long)]
    pub name: String,
}

/// Public interface for initializing logging.
pub fn init_logging(logging_environment: String) {
    logging::set_logging_environment(logging_environment);
    env_logger::init();
    log::info!("Starting fail2ban-monitoring");
}
