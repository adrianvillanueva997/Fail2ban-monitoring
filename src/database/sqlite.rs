use crate::database::driver::DatabaseDriver;
#[derive(Default)]
pub struct SqliteDriver {}

impl DatabaseDriver for SqliteDriver {
    fn connect(&self) {
        println!("Connected to MySQL");
    }
    fn close(&self) {}
}

impl SqliteDriver {
    pub fn new() -> Self {
        Self::default()
    }
}
