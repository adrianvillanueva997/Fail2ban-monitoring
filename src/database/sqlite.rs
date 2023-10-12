use crate::database::driver::DatabaseDriver;

struct SqliteDriver {}

impl DatabaseDriver for SqliteDriver {
    fn connect(&self) {}
}

impl SqliteDriver {}
