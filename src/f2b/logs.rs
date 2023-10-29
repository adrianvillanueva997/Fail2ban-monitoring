use std::fs::File;
use std::io::{BufRead, BufReader, Write};

// TODO: Refactor this function into separate functions.
fn process() {
    // Get the current date in YYYY-MM-DD format
    let date = chrono::Local::now().format("%Y-%m-%d").to_string();

    // Read the fail2ban log file
    let file = File::open("/var/log/fail2ban.log").unwrap();
    let reader = BufReader::new(file);

    // Filter the lines that contain the current date and extract the IP addresses
    let ips: Vec<String> = reader
        .lines()
        .filter_map(|line| {
            let line = line.unwrap();
            if line.contains(&format!("Ban {} ", date)) {
                let ip = line.split_whitespace().last().unwrap().to_string();
                Some(ip)
            } else {
                None
            }
        })
        .collect();

    // Write the IP addresses to a file
    let mut file = File::create("f2b.txt").unwrap();
    for ip in ips {
        writeln!(file, "{}", ip).unwrap();
    }
}
