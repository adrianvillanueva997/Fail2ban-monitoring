use crate::database::driver::DatabaseDriver;
#[derive(Default)]
pub struct MysqlDriver {}

impl DatabaseDriver for MysqlDriver {
    fn connect(&self) {
        println!("Connected to MySQL");
    }
    fn close(&self) {}
}

impl MysqlDriver {
    pub fn new() -> Self {
        Self::default()
    }
}
