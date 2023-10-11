use clap::Parser;
use fail2banmonitoring::init_logging;

/// The main function.
fn main() {
    let args = fail2banmonitoring::Args::parse();
    init_logging(args.logging_environment)
}
