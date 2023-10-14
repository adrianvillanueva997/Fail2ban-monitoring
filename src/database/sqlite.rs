use crate::database::driver::DatabaseDriver;
use sqlx::{migrate::MigrateDatabase, Sqlite};
use std::path::Path;
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

    /// Create a SQLite database.
    async fn create_sqlite_database(&self, database_name: &str) {
        let path = Path::new(database_name);
        if path.exists() {
            log::info!("SQLite database already exists: {}", database_name);
        } else {
            log::warn!("SQLite database does not exist: {}", database_name);
            match Sqlite::create_database("sqlite://sqlite.db").await {
                Ok(_) => {
                    log::info!("SQLite database created: {}", database_name);
                }
                Err(e) => {
                    log::error!("SQLite database creation failed: {}", e);
                }
            }
        }
    }
    async fn table_exists() -> bool {
        // TODO: Check if the table exists, if it does not exist run migrations
        false
    }
    async fn run_migrations() {}
}
