use crate::database::driver::DatabaseDriver;
#[derive(Default)]
pub struct PostgresDriver {}

impl DatabaseDriver for PostgresDriver {
    fn connect(&self) {
        println!("Connected to MySQL");
    }
    fn close(&self) {}
}

impl PostgresDriver {
    pub fn new() -> Self {
        Self::default()
    }
}
