use crate::database::driver::DatabaseDriver;

use sqlx::{migrate::MigrateDatabase, query::Query, Row, Sqlite, SqlitePool};
use std::path::Path;
use validator::Validate;
#[derive(Debug, Validate, Default)]
pub struct SqliteDriver {
    pub database_name: String,
    pub database_url: String,
    pub connection_pool: Option<sqlx::Pool<sqlx::Sqlite>>,
    // config: *const Config,
}

pub struct Test {}

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
    async fn create_sqlite_database(&self) {
        match Sqlite::database_exists(&self.database_url).await {
            Ok(_) => {
                log::info!("SQLite database already exists: {}", &self.database_name);
            }
            Err(e) => {
                log::error!("SQLite database does not exists, time to create it: {}", e);
                match Sqlite::create_database(&self.database_url).await {
                    Ok(_) => {
                        log::info!("SQLite database created: {}", &self.database_name);
                    }
                    Err(e) => {
                        log::error!("SQLite database creation failed: {}", e);
                    }
                }
            }
        }
    }
    async fn table_exists(&self) -> bool {
        let query: Query<sqlx::Sqlite, _> = sqlx::query(
            "-- sql
        SELECT name from sqlite_master where name='fail2banmonitoring' and type='table';",
        );
        let result = query
            .fetch_one(self.connection_pool.as_ref().unwrap())
            .await
            .unwrap();
        let a: String = result.get(0);
        false
    }
    async fn run_migrations(&self) {
        if self.table_exists().await {
            log::info!("SQlite table already exists.");
        } else {
            log::warn!("SQLite table does not exist, running migrations.");
        }
    }

    async fn create_connection_pool(&mut self) {
        let pool: Result<sqlx::Pool<Sqlite>, sqlx::Error> =
            SqlitePool::connect_lazy(&self.database_url);
        match pool {
            Ok(pool) => {
                self.connection_pool = Some(pool.clone());
                log::info!("SQLite connection pool created: {}", self.database_url);
            }
            Err(e) => {
                log::error!("SQLite connection pool creation failed: {}", e);
                panic!("SQLite connection pool creation failed: {}", e)
            }
        }
    }
}
