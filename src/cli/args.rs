use clap::{command, Parser};

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
