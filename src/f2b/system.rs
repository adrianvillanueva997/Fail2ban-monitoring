use std::process::Command;

pub fn is_f2b_installed() -> bool {
    Command::new("fail2ban-client").output().is_ok()
}
