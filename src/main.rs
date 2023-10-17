use clap::Parser;
use fail2banmonitoring::start_procedure;

/// The main function.
#[tokio::main]
async fn main() {
    let args = fail2banmonitoring::cli::args::Args::parse();
    start_procedure(args.logging_environment)
}
