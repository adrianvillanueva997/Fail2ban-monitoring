use crate::database::driver::DatabaseDriver;

struct MysqlDriver {}

impl DatabaseDriver for MysqlDriver {
    fn connect(&self) {
        println!("Connecting to MySQL...");
    }
}

impl MysqlDriver {
    // add code here
}
